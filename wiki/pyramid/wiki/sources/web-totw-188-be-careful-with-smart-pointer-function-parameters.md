---
type: source
source-type: web
title: "Tip of the Week #188: Be Careful With Smart-Pointer Function Parameters"
author: "Krzysztof Kosiński"
date: 2012
url: https://abseil.io/tips/188
summary: "abseil C++ Tips of the Week #188: Be Careful With Smart-Pointer Function Parameters."
tags: [cpp, abseil, totw, performance, idioms]
created: 2026-06-10
source-md5: c47056f77c36e9dd991b705cd2dd7f26
---

> 原文：<https://abseil.io/tips/188> · 作者：Krzysztof Kosiński · 发布：2012 · 内容许可：CC BY 4.0（abseil.io docs）
>
> 完整原文转录（脚注 [Tip \#NN](/tips/NN) 链接保留，邮件保护链接为 CloudFlare 默认转码无法还原）。

# Tip of the Week \#188: Be Careful With Smart-Pointer Function Parameters

\
\

Originally posted as TotW \#188 on December 10, 2020

*By [Krzysztof Kosiński](/cdn-cgi/l/email-protection#6d061f17141e04022d0a02020a0108430e0200)*

Updated 2020-12-10

Quicklink: [abseil.io/tips/188](https://abseil.io/tips/188)

What is wrong with this code?

```cpp

bool CanYouPetTheDog(const std::shared_ptr<Dog>& dog,
                     absl::Duration min_delay) {
  return dog->GetLastPetTime() + min_delay < absl::Now();
}
```

The function `CanYouPetTheDog` does not affect the ownership of its `dog` argument, yet its signature demands that it should be stored in a `std::shared_ptr`. This creates an unnecessary dependency on a specific ownership model, even though nothing in the function requires it. This dependency prevents callers from using other models, such as `std::unique_ptr` or constructing objects on the stack.

## Use References or Pointers When Ownership is Unaffected

By using a reference, we can remove the dependency on a specific ownership model, and allow our function to work with any object of type `Dog`.

```cpp

bool CanYouPetTheDog(const Dog& dog, absl::Duration min_delay) {
  return dog.GetLastPetTime() + min_delay < absl::Now();
}
```

With the above definition, the function can be called regardless of the caller’s ownership model:

```cpp

Dog stack_dog;
if (CanYouPetTheDog(stack_dog, delay)) { ... }

auto heap_dog = std::make_unique<Dog>();
if (CanYouPetTheDog(*heap_dog, delay)) { ... }

CustomPetPtr<Dog> custom_dog = CreateDog();
if (CanYouPetTheDog(*custom_dog, delay)) { ... }
```

If the function modifies the passed value, pass a mutable reference or a raw pointer, and use the same idioms as shown above.

## Use Smart Pointers When the Function Modifies Ownership

The following code provides several overloads for different smart pointer parameters. The first overload assumes ownership of the passed object and the second one adds a shared reference to the passed object. Both of these operations depend on how the caller handles ownership of the `Dog`. Adopting a `Dog` that lives on the stack isn’t possible, as ownership can’t be taken away from the stack.

```cpp

class Human {
 public:
  ...
  // Transfers ownership of `dog` to this Human.
  // See Tip #117 for the rationale for accepting std::unique_ptr by value.
  void Adopt(std::unique_ptr<Dog> dog) {
    pets_.push_back(std::move(dog));
  }
  // Adds a shared reference to `cat`.
  void Adopt(std::shared_ptr<Cat> cat) {
    pets_.push_back(std::move(cat));
  }

 private:
  std::vector<std::shared_ptr<Pet>> pets_;
  ...
};
```

## Conclusion

If ownership is not being transferred or modified, avoid having smart pointers as function parameters.

## See Also

- [Tip \#117](/tips/117)
- [C++ Core Guideline F.7](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#f7-for-general-use-take-t-or-t-arguments-rather-than-smart-pointers)
- [C++ Core Guideline R.30](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r30-take-smart-pointers-as-parameters-only-to-explicitly-express-lifetime-semantics)
- [Herb Sutter’s Guru of the Week \#91](https://herbsutter.com/2013/06/05/gotw-91-solution-smart-pointer-parameters/)


