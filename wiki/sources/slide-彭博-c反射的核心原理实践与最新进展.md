---
type: source
source-type: slide
title: "彭博_C++反射的核心原理实践与最新进展"
path: slides/彭博_C++反射的核心原理实践与最新进展.pdf
size: 3901 KB
category: slide
ingested: 2026-06-04
tool: liteparse
liteparse-version: 2.0.5
---

# 彭博_C++反射的核心原理实践与最新进展

> Ingested from `slides/彭博_C++反射的核心原理实践与最新进展.pdf` via `lit parse` on 2026-06-04.
> Source file: 3.81 MB.

## Page 1

_(no text content on this page)_

## Page 2

_(no text content on this page)_

## Page 3

_(no text content on this page)_

## Page 4

_(no text content on this page)_

## Page 5

_(no text content on this page)_

## Page 6

C++反射的核心原理、实践与最新进展

Overview of basic C++ reflection usages, applications, and ongoing work



Meya Zhao, Henry Haorong Yang, Zhenchao Lin

## Page 7

C++ Reflection 101
Overview of basic C++ reflection usages,
applications, and ongoing work

CPP-Summit
December 13, 2025

Meya Zhao, Henry Haorong Yang, Zhenchao Lin
Software Engineers, Real-Time Market Data Feeds

© 2025 Bloomberg Finance L.P. All rights reserved.

## Page 8

Who are we?

Bloomberg Feeds Engineering

 -   We design, build, and operate exchange
     and contributor facing real-time market
     data systems
 -   Our mandate is to model every exchange
     event, and propagate to downstream
     Bloomberg systems in real time
 -   We engineer for resiliency, low latency,
     and scale
 -   A single one of our many applications can
     process hundreds of millions of events in
     a day


     3

## Page 9

A problem in real-time market data pipelines
_________
Case study

FIX
message - received







34=1
60=20210830-12:34:56.789+08
55=AAPL
44=2.3
387=4




4

## Page 10

A problem in real-time market data pipelines
_________
Case study
FIX                          C++
message - received           object - represented
                             struct QuoteMessage {
                               unsigned long   MsgSeqNum;
                               sys_time<ms>    TransactTime;
                               std::string     Symbol;
                               double          Price;
                               int             Volume;
                             } myQuoteMessage {
34=1                           1,
60=20210830-12:34:56.789+08    2021-08-30 12:34:56.789,
55=AAPL                        "AAPL",
44=2.3                         2.3,
387=4                          4
                             };



                                               5

## Page 11

A problem in real-time market data pipelines
_________
Case study
FIX                          C++ JSON
message - received           object - represented object - serialized
                             struct QuoteMessage {
                                   unsigned long   MsgSeqNum;
                                   sys_time<ms>    TransactTime;
                                   std::string     Symbol;
                                   double          Price;
                                   int             Volume;
                             } myQuoteMessage { {
34=1                               1, "MsgSeqNum": 1,
60=20210830-12:34:56.789+08        2021-08-30 12:34:56.789, "TransactTime": 2021-08-30 12:34:56.789,
55=AAPL                            "AAPL", "Symbol": "AAPL",
44=2.3                             2.3, "Price": 2.3,
387=4                              4 "Volume": 4
                             }; }



                                                   6

## Page 12

Without reflection
 _________
 Case study: real-time market data parsing
 struct QuoteMessage { ... };
 template <> struct std::formatter<QuoteMessage, char> {
   // ...
   auto format(const QuoteMessage& msg, FormatContext& ctx) const
   {
       return std::format_to(
          ctx.out(),
          "{{\"MsgSeqNum\":     {}, \"TransactTime\": {:%F %T}, "
          "\"Symbol\": \"{}\", \"Price\": {}, \"Volume\": {}}}",
          msg.d_MsgSeqNum,
          // ...
          msg.d_Volume);
   }
 };


          7

## Page 13

Ideally…
 _________
 Case study: real-time market data parsing
 struct QuoteMessage { ... };


 struct json_formatter {
   // ...
   template <typename T>
   auto format(T const& t, auto& ctx) const { /* use reflection */ }
 };

 template <> struct std::formatter<QuoteMessage>  : json_formatter { };





   8

## Page 14

Ideally…
 _________
 Case study: real-time market data parsing
 struct QuoteMessage { ... };
 struct TradeMessage { ... };
 struct QuoteAndTradeMessage {     ... };

 struct json_formatter {
   // ...
   template <typename T>
   auto format(T const& t, auto& ctx) const { /* use reflection */ }
 };

 template <> struct std::formatter<QuoteMessage>         : json_formatter { };
 template <> struct std::formatter<TradeMessage>         : json_formatter { };
 template <> struct std::formatter<QuoteAndTradeMessage> : json_formatter { };



                                                  9

## Page 15

What’s in the offer?

  ● ^^ and [: :]
  ● std::meta::info

  ● meta functions

  ● Powerfully applied up to you…






  10

## Page 16

_________
What’s in the offer? 1/3

int main(){
     int i = 0;          ✓ ^^i - lift i into the
     return [: ^^i :];     reflection domain
}                        ✓ [: ^^i :] - splice ^^i back


     ✓     [:     ^^i :] == i
 Program returned: 0

         11

## Page 17

cat
   ^^cat










9
 Source of generated images on this slide: ChatGPT

## Page 18

        cat
[: ^^cat :]    ^^cat










    10
      Source of generated images on this slide: ChatGPT

## Page 19

             cat     ^^cat
   [: reflCat :]     reflCat



^^reflCat    [: ^^reflCat :]






   11
                     Source of generated images on this slide: ChatGPT

## Page 20

std::meta::info
 _________
 What’s in the offer? 2/3
 int main() {
  int i     = 0;
  constexpr std::meta::info r = ^^i;
  return [: r :];
 }

  Program returned: 0

      15

## Page 21

Cat     std::meta::info
cat     ^^cat
        reflCat










13
        Source of generated images on this slide: ChatGPT

## Page 22

               Cat     std::meta::info
               cat     ^^cat
    [: reflCat :]      reflCat

std::meta::info
^^reflCat




               [: ^^reflCat :]










14
                       Source of generated images on this slide: ChatGPT

## Page 23

meta functions
_________
What’s in the offer? 3/3










18

## Page 24

                    ??? std::meta::info
                    cat ^^cat

    typename Cat std::meta::info
type_of(^^cat)










    16
                    Source of generated images on this slide: ChatGPT

## Page 25

meta functions
_________
What’s in the offer? 3/3

int main() {
    int i = 0;
    constexpr auto r = ^^i;
    if constexpr (std::is_same_v<
     typename [: std::meta::type_of(r) :], int>) return 0;
    return 1;
}

 Program returned: 0

 ___________        20
 Note: All meta functions are consteval. C++ reflection is compile time.

## Page 26

What can we do with ^^ and [: :]?





21

## Page 27

  meta functions - access members
  _________
  What’s in the offer? 3/3

  #include <meta>

namespace std::meta {
    consteval auto nonstatic_data_members_of(
           info           r, // Reflected (struct) type
       access_context ctx // Access context
   ) -> vector<info>;        // List of reflected members
  }


   Note: All meta functions are consteval. C++ reflection is compile time.    22

## Page 28

  meta functions - access context
  _________
  What’s in the offer? 3/3

  You may have seen or used this interface:

[[deprecated(
    "P2996R10 requires an 'access_context' argument")]]
consteval auto nonstatic_data_members_of(info r) -> vector<info> {
    return nonstatic_data_members_of(
       r, access_context::unchecked());
}

  How to use access_context?

   Note: All meta functions are consteval. C++ reflection is compile time.    23

## Page 29

meta functions - access context cont.
 _________
 What’s in the offer? 3/3

 struct access_context {
   consteval access_context(
       info scope, info designating_class) noexcept;
   …
   static consteval access_context current()                         noexcept;
   static consteval access_context unprivileged() noexcept;
   static consteval access_context unchecked()                       noexcept;
   …
 };

 Definitions from p2996r13:

   “The access_context class is a non-aggregate type that represents a namespace, class, or function from which
   queries pertaining to access rules may be performed, as well as the designating class, if any.”

   Note: All meta functions are consteval. C++ reflection is compile time.        24

## Page 30

                                                                             struct User {
                                                                               std::string  name;
meta functions - unchecked context                                             unsigned long id;
 _________                                                                   private:
 What’s in the offer? 3/3                                                      std::string  address;
 constexpr auto reflectedMembers =                                           };
  define_static_array(     // recall what kind of type it returns?
     std::meta::nonstatic_data_members_of(
              ^^User,
              std::meta::access_context::unchecked()));

 static_assert(reflectedMembers.size() == 3);
 static_assert(^^User::name == reflectedMembers[0]);
 static_assert(^^User::id                            == reflectedMembers[1]);

 static consteval bool User::CheckPrivateMember(std::meta::info i) {
  return i == ^^address;     // can’t directly access private member
 }
 static_assert(User::CheckPrivateMember(reflectedMembers[2]));

  Note: All meta functions are consteval. C++ reflection is compile time.          25

## Page 31

                                                                struct User {
                                                                  std::string  name;
meta functions - current context                                  unsigned long id;
_________                                                       private:
What’s in the offer? 3/3                                          std::string  address;
constexpr auto reflectedMembers =                               };
define_static_array(
    std::meta::nonstatic_data_members_of(
             ^^User,
             std::meta::access_context::current()));

static_assert(reflectedMembers.size() == 2);
static_assert(^^User::name == reflectedMembers[0]);
static_assert(^^User::id    == reflectedMembers[1]);

// static_assert(User::CheckPrivateMember(reflectedMembers[2]));





Note: All meta functions are consteval. C++ reflection is compile time.    26

## Page 32

                                                              struct User {
                                                                std::string  name;
meta functions - current context cont.                          unsigned long id;
 _________                                                    private:
 What’s in the offer? 3/3                                       std::string  address;
 static consteval auto User::ReflectedMembers() {             };
  return define_static_array(
     std::meta::nonstatic_data_members_of(
              ^^User,
              std::meta::access_context::current()));
 }
 constexpr auto reflectedMembers = User::ReflectedMembers();

 static_assert(reflectedMembers.size() == 3);
 static_assert(^^User::name == reflectedMembers[0]);
 static_assert(^^User::id    == reflectedMembers[1]);
 static_assert(User::CheckPrivateMember(reflectedMembers[2]));




 Note: All meta functions are consteval. C++ reflection is compile time.    27

## Page 33

                                                                struct User {
                                                                  std::string  name;
meta functions - unprivileged context                             unsigned long id;
_________                                                       private:
What’s in the offer? 3/3                                          std::string  address;
constexpr auto reflectedMembers =                               };
define_static_array(
    std::meta::nonstatic_data_members_of(
             ^^User,
             std::meta::access_context::unprivileged()));

static_assert(reflectedMembers.size() == 2);
static_assert(^^User::name == reflectedMembers[0]);
static_assert(^^User::id   == reflectedMembers[1]);

// static_assert(User::CheckPrivateMember(reflectedMembers[2]));




Note: All meta functions are consteval. C++ reflection is compile time.    28

## Page 34

                                                             struct User {
                                                               std::string  name;
meta functions - unprivileged context cont.                    unsigned long id;
 _________                                                   private:
 What’s in the offer? 3/3                                      std::string  address;
 static consteval auto User::ReflectedMembers() {            };
  return define_static_array(
     std::meta::nonstatic_data_members_of(
              ^^User,
              std::meta::access_context::unprivileged()));
 }
 constexpr auto reflectedMembers = User::ReflectedMembers();

 static_assert(reflectedMembers.size() == 2);
 static_assert(^^MessageHeader::name == reflectedMembers[0]);
 static_assert(^^MessageHeader::id  == reflectedMembers[1]);
 // static_assert(MessageHeader::CheckPrivateMember(reflectedMembers[2]));




 Note: All meta functions are consteval. C++ reflection is compile time.    29

## Page 35

                                                              struct User {
                                                                std::string  name;
meta functions - access context summary                         unsigned long id;
_________                                                     private:
What’s in the offer? 3/3                                        std::string  address;
                                                              };
For private members in a class, when

             Access Context Type     In class     Out of class

             unchecked               Yes          Yes

             current                 Yes          No

             unprivileged            No           No

For simplicity, we are going to use unchecked in later examples


Note: All meta functions are consteval. C++ reflection is compile time.    30

## Page 36

                                                                              struct User {
                                                                                std::string name;
  meta functions - identifier                                                   unsigned long id;
  _________                                                                   private:
  What’s in the offer? 3/3                                                      std::string address;
  #include     <meta>                                                         };

namespace std::meta {
   consteval auto identifier_of(info) -> string_view;
}

  std::cout    << std::meta::identifier_of(^^User::name);

  Output: name

   Note: All meta functions are consteval. C++ reflection is compile time.          31

## Page 37

                                                                                struct User {
                                                                                  std::string  name;
    meta functions - identifier cont.                                             unsigned long id;
    _________                                                                   private:
    What’s in the offer? 3/3                                                      std::string  address;
    constexpr auto reflectedMembers =                                           };
std::define_static_array(
         std::meta::nonstatic_data_members_of(
                 ^^User,
                 std::meta::access_context::unchecked())); // for simplicity

    template for (constexpr std::meta::info data_member : reflectedMembers) {
     std::cout << std::meta::identifier_of(data_member) << std::endl;
    }

    Output:
     name
     id
     address

     Note: All meta functions are consteval. C++ reflection is compile time.          32

## Page 38

meta functions - base class
_________
What’s in the offer? 3/3

#include  <meta>

namespace std::meta     {
 consteval     auto     bases_of(
         info        class_type, // Reflected derived type
         access_context  ctx     // Access context
 ) -> vector<info>;              // List of reflected base types
}


 Note: All meta functions are consteval. C++ reflection is compile time.    33

## Page 39

                                                     struct Base1 { … };
                                                     struct Base2 { … };
meta functions - base class cont.                    struct Derive : Base1, Base2 {
 _________
 What’s in the offer? 3/3                              …
 template for (                                      };
  constexpr std::meta::info data_member :
  define_static_array(
      std::meta::bases_of(
          ^^Derive,
          std::meta::access_context::unchecked()))) {
  std::cout << std::meta::identifier_of(std::meta::type_of(data_member));
 }

 Output:
  Base1
  Base2


  Note: All meta functions are consteval. C++ reflection is compile time.    34

## Page 40

  meta functions - enum
  _________
  What’s in the offer? 3/3

  #include <meta>

namespace std::meta {
   consteval auto enumerators_of(
       info enum_type // Reflected enum type
   ) -> vector<info>; // List of reflected enum members
}



   Note: All meta functions are consteval. C++ reflection is compile time.    35

## Page 41

                                                                             enum class Color: char {
meta functions - enum cont.                                                    Red  = '1',
 _________                                                                     Green = '2'
 What’s in the offer? 3/3                                                    };
 constexpr Color qs = Color::Red;
 static_assert(std::meta::enumerators_of(^^Color)[0] == ^^Color::Red);
 static_assert(std::meta::enumerators_of(^^Color)[1] == ^^Color::Green);

 template for (constexpr auto e : define_static_array(
  std::meta::enumerators_of(^^Color))) {
  if constexpr ([: e :] == qs) {
  std::cout << std::meta::identifier_of(e) << std::endl;
  }
 }

 Output: Red
  Note: All meta functions are consteval. C++ reflection is compile time.        36

## Page 42

Time to assemble our formatters with reflections!








37

## Page 43

JSON Serializer with reflection
 _________
 Case study: real-time market data parsing

 struct QuoteMessage { ... };
 struct TradeMessage { ... };
 struct QuoteAndTradeMessage {     ... };

 struct json_formatter {
   // ...

   template <typename T>
   auto format(T const& t, auto& ctx) const {
       // use reflection
   }
 };

 template <> struct std::formatter<QuoteMessage>         : json_formatter { };
 template <> struct std::formatter<TradeMessage>         : json_formatter { };
 template <> struct std::formatter<QuoteAndTradeMessage> : json_formatter { };
                                                      38

## Page 44

How does it work?
 _________
 Build a universal JSON formatter with reflection

 struct QuoteMessage { ... };
 struct TradeMessage { ... };
 struct QuoteAndTradeMessage { ... };

 struct json_formatter {
   // ...

   template <typename T>
   auto format(T const& t, auto& ctx) const {
       // use reflection
   }
 };

 template <> struct std::formatter<QuoteMessage>         : json_formatter { };
 template <> struct std::formatter<TradeMessage>         : json_formatter { };
 template <> struct std::formatter<QuoteAndTradeMessage> : json_formatter { };
                                                      39

## Page 45

                                                                    QuoteMessage message {
                                                                            1,
                                                                            2021-08-30 12:34:56.789,
Step 1/3: Print all data members …                                          "AAPL",
 _________                                                                  2.3,
 Build a universal JSON formatter with reflection                           4
 struct json_formatter {                                            };
   template <typename T>
   auto format(T const& t, auto& ctx) const {
              auto out = ctx.out();
              *out++ = '{';
              // Give access to all members, including protected and private
              constexpr auto access = std::meta::access_context::unchecked();
              template for (
               constexpr std::meta::info data_member : std::define_static_array(
               std::meta::nonstatic_data_members_of(^^T, access))) {
               delim(); // Defined outside
               out = std::format_to(out, "{}", t.[: data_member :]);
              }
              *out++ = '}';
              return out;
   }
 };
 Output: {1,   2021-08-30 12:34:56.789, AAPL,     2.3, 4}                       40

## Page 46

                   QuoteMessage message {
                                                                            1,
                                                                            2021-08-30 12:34:56.789,
Step 1/3: Print all data members …                                          "AAPL",
 _________                                                                  2.3,
 Build a universal JSON formatter with reflection                           4
 struct json_formatter {        };
   template <typename T>
   auto format(T const& t, auto& ctx) const {
              auto out = ctx.out();
              *out++ = '{';
              // Give access to all members, including protected and private
              constexpr auto access = std::meta::access_context::unchecked();
              template for (
               constexpr std::meta::info data_member : std::define_static_array(
               std::meta::nonstatic_data_members_of(^^T, access))) {
               delim(); // Defined outside
               out = std::format_to(out, "{}", t.[: data_member :]);
              }
              *out++ = '}';
              return out;
   }
 };
 Output: {1,   2021-08-30 12:34:56.789, AAPL,     2.3, 4}                       41

## Page 47

                                                           QuoteMessage message {
                                                             1,
                                                             2021-08-30 12:34:56.789,
Step 2/3: … with their identifiers                           "AAPL",
 _________                                                   2.3,
 Build a universal JSON formatter with reflection            4
 template for (                                            };
      constexpr std::meta::info data_member :
           std::define_static_array(std::meta::nonstatic_data_members_of(^^T, access))) {
      delim();
      if constexpr (std::meta::has_identifier(data_member)) {
                   out = std::format_to(out, "\"{}\":  ", std::meta::identifier_of(data_member));
      } else {
                   out = std::format_to(out, "\"{}\":  ", std::format("(unnamed-member-{})", count++)));
      }
      out = std::format_to(out, "{}", t.[: data_member :]);
 }
 Output:
 {     "MsgSeqNum": 1,
       "TransactTime": 2021-08-30 12:34:56.789,
       "Symbol": AAPL,
       "Price": 2.3,
 }     "Volume": 4                                               42

## Page 48

Step 3/3: How about enums?
_________
Build a universal JSON formatter with reflection

struct Quote {
     double     Price;                           Output:
     char       Side; // '1' for bid, '2' for ask
};   int        Volume;                          {  "MsgSeqNum": 1,
struct QuoteMessage {                               "SendingTime": 2021-08-30 12:34:56.789,
     unsigned long             MsgSeqNum;
     sys_time<milliseconds>    SendingTime;         "Symbol": GOOG,
     std::string               Symbol;              "Quotes": [
     std::vector<Quote>        Quotes;                 { "Price": 1.2, "Side": 1, "Volume": 3 },
} {  1,                                             ]  { "Price": 4.5, "Side": 2, "Volume": 6 }
     2021-08-30 12:34:56.789, // pseudo
     "GOOG",                                     }
     {
            Quote{1.2, '1', 3},
            Quote{4.5, '2', 6}
     }
} myQuoteMessage;
                                                           43

## Page 49

Step 3/3: How about enums?
_________
Build a universal JSON formatter with reflection
enum QuoteSide : char {
   Bid = '1', Ask = '2'
};
struct Quote {
   double Price;
   QuoteSide Side;
   int     Volume;
};
struct QuoteMessage {
   unsigned long            MsgSeqNum;
   sys_time<milliseconds>   SendingTime;
   std::string              Symbol;
   std::vector<Quote>       Quotes;
} {
   1,
   2021-08-30 12:34:56.789, // pseudo
   "GOOG",
   {
        Quote{1.2, QuoteSide::Bid, 3},
        Quote{4.5, QUoteSide::Ask, 6}
   } 44
} myQuoteMessage;

## Page 50

Step 3/3: How about enums? without reflection
_________
Build a universal JSON formatter with reflection
enum QuoteSide : char {
      Bid = '1', Ask = '2'
};
struct Quote {
      double Price;
      QuoteSide Side; auto format(const QuoteSide& qs, FormatContext& ctx) const {
      int         Volume; return std::format_to(
}; ctx.out(), "{}",
struct QuoteMessage { qs == QuoteSide::Bid ? "Bid" : "Ask");
      unsigned long           MsgSeqNum; }
      sys_time<milliseconds>  SendingTime;
      std::string             Symbol;
      std::vector<Quote>      Quotes;
} {
      1,
      2021-08-30 12:34:56.789, // pseudo
      "GOOG",
      {
           Quote{1.2, QuoteSide::Bid, 3},
           Quote{4.5, QuoteSide::Ask, 6}
      } 45
} myQuoteMessage;

## Page 51

  Step 3/3: How about enums? with reflection
   _________
   Build a universal JSON formatter with reflection

template<typename E> requires std::is_enum_v<E>
constexpr std::string enum_to_string(E enumValue) {
    template for (constexpr auto e :
       std::define_static_array(std::meta::enumerators_of(^^E))){
       if (enumValue == [: e :]) return std::string(std::meta::identifier_of(e));
    }
    return std::to_string(std::to_underlying(enumValue));
}







            46

## Page 52

  Step 3/3: How about enums?                             with reflection
   _________
   Build a universal JSON formatter with reflection

template for (constexpr auto data_member :
       std::define_static_array(std::meta::nonstatic_data_members_of(^^T, access))) {
    delim();
    // ...
    out = std::format_to(out, "\"{}\": ", mem_label);
    if constexpr (std::is_enum_v<std::remove_cvref_t<
       typename [: std::meta::type_of(data_member) :]>>) {
                          out = std::format_to(out,  "\"{}\"", enum_to_string(t.[: data_member :]));
    } else {
                          out = std::format_to(out,  "{}", t.[: data_member :]);
    }
   }


                                                     47

## Page 53

Step 3/3: How about enums?                                   with reflection
_________
Build a universal JSON formatter with reflection
enum QuoteSide : char {                         Output:
      e_Bid = '1', e_Ask = '2'
};
struct Quote {                                  {
      double     Price;                           "MsgSeqNum": 1,
      QuoteSide Side;                             "SendingTime": 2021-08-30 12:34:56.789,
      int           Volume;                       "Symbol": "GOOG",
};                                                "Quotes": [
struct QuoteMessage {                                  {
      unsigned long            MsgSeqNum;                 "Price": 1.2,
      sys_time<milliseconds>   SendingTime;               "Side": "Bid",
      std::string              Symbol;
      std::vector<Quote>       Quotes;                    "Volume": 3
} myQuoteMessage {                                     },
      1,                                               {
      2021-08-30 12:34:56.789, // pseudo                  "Price": 4.5,
      "GOOG",                                             "Side": "Ask",
      {      Quote{1.2, QuoteSide::Bid, 3},            }  "Volume": 6
};    }      Quote{4.5, QuoteSide::Ask, 6}      } ]           48

## Page 54

Is that all for Reflections?

What’s more in C++ community in Bloomberg?




49

## Page 55

Attribute Reflection (P3385)

https://wg21.link/P3385
Author: Aurelien Cassagnes






^^[[nodiscard]]










50

## Page 56

  What Attribute Reflections Provide

  constexpr auto stdAttr = ^^[[nodiscard("example")]];
  struct [[deprecated]] MyStruct {};

  We shall be able to:

- Reflect an attribute token: ^^[[deprecated]] → info
- Enumerate instances on an entity: std::meta::attributes_of(^^MyStruct) → vector<info>
- Inspect attribute: static_assert(std::meta::identifier_of(stdAttr) == "nodiscard");
- And more…

  Attributes are already widely used, and enabling metaprogramming of attributes unlocks many utilities.



  51

## Page 57

Basic Examples

std::meta::is_attribute(info r)
-> bool

static_assert(std::meta::is_attribute(^^[[nodiscard]]));     std::meta::attributes_of(info r)
                                                             -> vector<info>

                                                             enum class [[nodiscard("Error discarded")]] ErrorCode {
std::meta::has_attribute(info construct,                    Disconnected,
                                 info attribute)            ConfigurationIncorrect,
                                                            OutdatedCredentials,
-> bool                                                      };
struct [[clang::consumable(unconsumed)]] F {                 static_assert(std::meta::attributes_of(^^ErrorCode)[0]
[[clang::callable_when(unconsumed)]] void f() {}            == ^^[[nodiscard("Error discarded")]]);
};

static_assert(std::meta::has_attribute(^^F::f,
^^[[clang::callable_when(unconsumed)]]));



                                                             52

## Page 58

                                        2: Perform define_aggregate

    define
    _aggregate                          constexpr auto ctx = std::meta::access_context::current();
                                        template<class T>
                                        struct MigratedT {
                                       struct impl;
                                       consteval {
1: We have defined a class User        std::vector<std::meta::info> migratedMembers = {};
                                       for (auto member : std::meta::nonstatic_data_members_of(^^T, ctx)) {
struct User {                             if (!std::meta::has_attribute(member, ^^[[deprecated]])) {
[[deprecated]] std::string name;           migratedMembers.push_back(std::meta::data_member_spec(
[[deprecated]] std::string country;        std::meta::type_of(member),
std::string uuidv5;                        {.name = std::meta::identifier_of(member)}
std::string countryIsoCode;                ));
};                                     }  }
                                       std::meta::define_aggregate(^^impl, migratedMembers);
                                       }
                                        };

3: Equivalent to if we have defined     using MigratedUser = MigratedT<User>::impl;
MigratedUser as below:                  static_assert(
                                       std::meta::nonstatic_data_members_of(^^User, ctx).size() == 4);
struct MigratedUser {                   static_assert(
std::string uuidv5;                    std::meta::nonstatic_data_members_of(^^MigratedUser, ctx).size() == 2);
std::string countryIsoCode;
};                                      - Possible use cases:
                                          - Zero-cost schema evolution
                                          - Compile-time enforcement (no touching deprecated field)        53

## Page 59

Implementing in Clang

Clang                     libcxx
(the compiler itself)     meta
clang/include/*
clang/lib/*

    compiles





                          Program being compiled
                          myapp.cpp




                          54

## Page 60

Implementing in Clang

Clang                            libcxx
(the compiler itself)            meta
clang/include/*                  consteval auto is_attribute(info r)
clang/lib/*                      ...
                                 consteval auto has_attribute(...
Implementation callbacks         ...
    compiles                     consteval auto attributes_of(info r)
...                              ...
static bool is_attribute(...
...
static bool has_attribute(...
...
static bool attributes_of(...
...
And all other compiler logic     Program being compiled
...                              myapp.cpp

                                 struct [[deprecated]] Foo {};
                                 constexpr auto rf = ^^Foo;

                                     55

## Page 61

    Implementing in Clang
    Lexer     Recognizes tokens in reflection expression
              e.g. ^^[[deprecated]]

              lib/Parse/ParseReflect.cpp:
    Parser    Parser::ParseCXXReflectExpression
              Parser::MaybeParseCXX11Attributes


              lib/Sema/SemaReflect.cpp:
Semantic      Sema::BuildCXXReflectExpr
Analysis     Stores ParsedAttr in CXXReflectExpr;
             Able to be retrieved for constant evaluation;



              56

## Page 62

    Implementing in Clang
    Lexer     Recognizes tokens of metafunction
              e.g. std::meta::is_attribute(...)

              lib/Parse/ParseReflect.cpp:
    Parser    Parser::ParseCXXMetafunctionExpression



                  lib/Sema/SemaReflect.cpp:
                  Sema::BuildCXXMetafunctionExpr
    Semantic
Analysis

    Constant Evaluation ExprConstant.cpp: VisitCXXMetafunctionExpr

                  ExprConstantMeta.cpp: is_attribute(...)
                  57

## Page 63

    Implementing in Clang (Summary)

 libcxx    Lexer    Parser    Semantic  Constant
 <meta>        Analysis      Evaluation



- libc++ / <meta>: Declare the new API and forward it to entry point
- Lexer: Ensure token is recognized. (reuse existing tokens)
- Parser: Recognize the call shape and build an AST node. (no evaluation yet)
- Semantic analysis: Wire the node to an implementation, validate argument kinds / access rules.
- Constant evaluation: Implement the callback: evaluate and produce the compile-time result.





    58

## Page 64

Useful links

P2996: https://wg21.link/P2996
P3385: https://wg21.link/P3385
Code example: https://godbolt.org/z/xs455rxnd









 © 2025 Bloomberg Finance L.P. All rights reserved.

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[slides/彭博_C++反射的核心原理实践与最新进展.pdf]]`
