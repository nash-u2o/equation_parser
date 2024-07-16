## Parser
### Why not use eval()?
This parser has been created to allow programs to evaluate equations without using Python's eval function, which has vulnerabilities allowing users to inject malicious code. 
### How does it work?
This parser takes equations in infix notation, the notation we are used to seeing equations, and converts them to postfix notation using the [Shunting Yard Algorithm](https://en.wikipedia.org/wiki/Shunting_yard_algorithm). It then uses a stack and queue to evaluate the postfix expression
### Usage
Pass an equation as a string to the process_equation method. It returns the result of the expression as a numpy longdouble.
### Adding functionality
As of right now, this parser does not support every function that could potentially be used. Generally, more complex functions aren't supported yet. Luckily, they are quite easy to implement should you need them! Place the function's name in the functions array near the top of the program and define its behavior in _eval_function()