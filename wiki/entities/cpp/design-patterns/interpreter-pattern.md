---
type: entity
tags: [cpp, design-patterns, behavioral]
created: 2026-05-27
sources: [github-liuzengh-design-pattern]
---

# Interpreter Pattern (解释器模式)

## GoF 定义

定义一个语法解释器，专门处理一种特定语言文法。

## C++ 实现

### 词法分析 → Token 流

```cpp
struct Token {
    enum Type { integer, plus, minus, lparen, rparen } type;
    string text;
    explicit Token(Type t, const string& tx) : type(t), text(tx) {}
};

vector<Token> lex(const string& input) {
    vector<Token> result;
    for (int i = 0; i < input.size(); ++i) {
        switch (input[i]) {
            case '+': result.emplace_back(Token{Token::plus, "+"}); break;
            case '-': result.emplace_back(Token{Token::minus, "-"}); break;
            case '(': result.emplace_back(Token{Token::lparen, "("}); break;
            case ')': result.emplace_back(Token{Token::rparen, ")"}); break;
            default:
                if (isdigit(input[i])) {
                    ostringstream buffer;
                    buffer << input[i];
                    for (int j = i + 1; j < input.size() && isdigit(input[j]); ++j)
                        buffer << input[j], i = j;
                    result.emplace_back(Token{Token::integer, buffer.str()});
                }
        }
    }
    return result;
}
```

### 语法分析 → AST

```cpp
struct Element { virtual int eval() const = 0; };

struct Integer : Element {
    int value;
    explicit Integer(int v) : value(v) {}
    int eval() const override { return value; }
};

struct BinaryOperation : Element {
    enum Type { addition, subtraction } type;
    shared_ptr<Element> lhs, rhs;
    int eval() const override {
        return type == addition ? lhs->eval() + rhs->eval() : lhs->eval() - rhs->eval();
    }
};

shared_ptr<Element> parse(const vector<Token>& tokens) {
    auto result = make_shared<BinaryOperation>();
    bool have_lhs = false;
    for (size_t i = 0; i < tokens.size(); ++i) {
        switch (tokens[i].type) {
            case Token::integer: {
                int val = stoi(tokens[i].text);
                auto integer = make_shared<Integer>(val);
                if (!have_lhs) { result->lhs = integer; have_lhs = true; }
                else result->rhs = integer;
                break;
            }
            case Token::plus: result->type = BinaryOperation::addition; break;
            case Token::minus: result->type = BinaryOperation::subtraction; break;
            case Token::lparen: /* 递归解析子表达式 */ break;
        }
    }
    return result;
}
```

## 关键点

- 解释器模式将文本转换为 AST 树结构
- 词法分析（Lexer）产生 Token 流，语法分析（Parser）构建 AST
- 工业级解析用 ANTLR / Boost.Spirit，而非手写

## 相关模式

- [[composite-pattern]]
- [[visitor-pattern]]
