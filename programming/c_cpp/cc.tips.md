1. (Linux) 查看当前编译的默认支持版本

```bash
:~$ gcc -dM -E -x c /dev/null | grep -F STDC_VERSION
#define __STDC_VERSION__ 201710L
:~$ g++ -dM -E -x c++ /dev/null | grep -F __cplusplus
#define __cplusplus 201703L
```
