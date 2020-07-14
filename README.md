pre-commit hook to remove cell output of .ipynb notebook and some metadata for better security.

Sample config:
```
repos:
  - repo: https://github.com/Zoynels/pre-commit-jupyter
    rev: v2.0.0
    hooks:
      - id: zs-jupyter-notebook-cleanup
        name: zs-jupyter-notebook-cleanup
        language: python
        entry: zs-jupyter-notebook-cleanup
        args:
          - --diff
          - --inplace
          - --remove-outputs
          - --remove-execution-count
          - --remove-empty-cell
          - --remove-spaces-cell
          - --remove-cell-metadata-patterns
          - "scrolled"
          - "collapsed"
          - "execution"
          - "ExecuteTime"
          - --pin-patterns
          - "[pin];[donotremove]"
        files: \.ipynb$
        types: ["file"]
```

If you have "pin patterns", You can keep cell outputs like that:

```
# [pin]
some_function()
print("some info")
```

```
# [donotremove]
some_function()
print("some info")
```

Thanks for first version to https://github.com/roy-ht/pre-commit-jupyter
