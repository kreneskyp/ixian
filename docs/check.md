# Checks

Checker determine whether a task is complete or not. Tasks may have zero or 
more checkers. There is no default checker, tasks will execute always. Adding a 
checker allows the task to be skipped if it is already complete. There are 
built-in checkers and an api for creating custom checkers.

Task dependencies are also checked. Branches that are complete will be skipped.
Checks cascade from dependencies. If a dependency is rebuilt, that branch and 
the root will be rebuilt. 

Checkers may be overridden with `--force` or implicitly with `--clean`. Use 
`--force-all` or `--clean` to override dependency checks too.

To view the status of checks use `--TODO not implemented yet`.

## Custom Checkers

Custom checkers may be created by subclassing `Checker` and implementing 
`state`, `filename`, and `clone`.

```python
from power_shovel.checker import Checker


class MyChecker(Checker):
    
    def state(self):
        return {'fake': 'state'}
        
    def filename(self):
        return 'custom_checker'
        
    def clone(self):
        pass 
```

#### State

`state` must return an object representing the state being checked. Generally,
this should be a hash or a dict of hashes. The state should accurately 
represent the changes you want to include. For example, a file checker might
return a hash of one or morefiles file's contents but ignore permission flags.

#### Filename

`filename` returns a deterministic filename for the input to the checker. All 
state is stored in json files located in `CONFIG.BUILDER/filename`. The 
contents are the `state` from the last successful run. The current state will
be compared against the stored value during subsequent runs.

#### Clone

`clone` must return a copy of the checker with the same parameters.  

TODO: This was to support checkers that cached properties. This may not be used
any longer so it can probably go away.

### Checker Storage

All state is stored in json files located in `CONFIG.BUILDER/checks`. If a 
state file doesn't exist a task is incomplete.


## Checker Subclasses

### SingleKeyChecker

`SingleKeyChecker` is a helper subclasses that implements support for hashing
a single input (key). 

```python
from power_shovel.checker import SingleKeyChecker

class MyChecker(SingleKeyChecker):

    def state(self):
        return 'fake_state'



check = MyChecker('fake_key')
```


`filename` returns a hash of the single key. 

`state` must be implemented by subclasses.



### MultiValueChecker

`MultiValueChecker` is a helper subclass that implements support for multiple
inputs of the same type. For example, it is used by [FileHash](#FileHash) to 
support multiple paths. 

```python
from power_shovel.checker import MultiValueChecker

class MyChecker(MultiValueChecker):

    def state(self):
        return 'fake_state'



check = MyChecker('fake_key_1', 'fake_key_2')
```

`filename` returns a hash of the list of keys

`state` must be implemented by subclasses.


## Built-in Checkers 


### FileHash

FileHash checks the sha256 hash for a set of file paths. Paths may point to 
files or directories.

```
from power_shovel.check import FileHash

Checker(
   '/path/to/my/file',
   '/path/to/my/other/file',
   '/path/to/my/directory',
   '/wildcard/*'
)
```

File hashes are a sha256 hash including the permissions, contents, and uid/gid 
flags for the file.

Directory hashes include the names and hashes of each file and directory the
directory contains. Directory permissions, uid, and gid are also hashed.
 
Paths may contain unix style wildcards. Wildcard patterns will hash the set of
files that match including the filenames.
