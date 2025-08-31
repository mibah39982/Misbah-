# file: README.md

# Roadman Programming Language

Wagwan! Welcome to the official repo for the Roadman Programming Language. It's a dynamic, interpreted language built in Python, bringing a bit of street slang to the world of coding.

## Language Features

*   **Dynamic Typing**: Variables are declared with `gimme` (mutable) or `conste` (immutable).
*   **Familiar Syntax**: C-style syntax with `{}` for blocks and `;` for statement termination.
*   **Core Constructs**: Supports functions (`fam`), if/else (`innit`/`elseway`), loops (`loopz`), and lists.
*   **Built-in I/O**: `say()` for printing to the console.
*   **Simple & Interpreted**: Runs directly via a Python-based tree-walk interpreter.

## Installation

To get started, you'll need Python 3.10+.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/roadman-lang.git
    cd roadman-lang
    ```

2.  **Install dependencies:**
    The only dependency is `pytest` for running tests.
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

You can run Roadman code in two ways: through the interactive REPL or by executing a `.road` file.

### Interactive REPL

To start the Read-Eval-Print Loop (REPL), run:
```bash
python -m src.repl
```
You'll be greeted with a prompt. You can type Roadman code directly here.

**REPL Demo:**
```
$ python -m src.repl
Roadman REPL v0.1
Type 'exit()' or press Ctrl+C to exit.
> say("Wagwan");
Wagwan
> gimme x = 10 * 2;
> say(x);
20.0
> exit()
```

### Running a File

To execute a Roadman script file (e.g., `examples/hello.road`), use the runner:
```bash
python -m src.runner examples/hello.road
```
This will run the code in the file and print any output to the console.

## Testing

The project comes with a test suite for the lexer, parser, and interpreter. To run the tests, use `pytest`:
```bash
pytest
```
You should see all tests passing, confirming that the language components are working correctly.

## Example: Factorial

Here's a quick look at a factorial function written in Roadman:

```roadman
# file: examples/fact.road

// A function to calculate the factorial of a number recursively.
fam factorial(n) {
    // Base case: if n is less than 2, factorial is 1.
    innit (n < 2) {
        returnz 1;
    }
    // Recursive step.
    returnz n * factorial(n - 1);
}

say(factorial(7)); // Outputs: 5040.0
```

---
Built with vibes. — ROADMAN dev