# First Time Java Script Assessment: 

## Goals: 
	* Understand the logic and the sintax for the java script exercice.
	* Understand the use of operators, loops and functions during the exercice.
	* Explain the exercice over the class room or in a technical enterview.

## Momento 1 — Control Structures and Functions

This assessment focuses on understanding and applying fundamental JavaScript programming concepts through a simple login simulation.

The exercise is developed using **pure JavaScript** and is intended to be executed directly in the **browser console**.

---

## Goals

- Understand JavaScript logic and syntax.
- Understand and apply variables.
- Understand comparison and logical operators.
- Practice conditional structures.
- Practice loops and iteration.
- Understand and apply functions.
- Understand encapsulation of program logic.
- Develop a simple sequential program flow.
- Explain the exercise in the classroom using a technical approach.

---

## Assessment Objective

The objective of this exercise is to validate the understanding and application of logical control structures:

- Variables
- Conditionals
- Loops
- Functions
- Encapsulation

The program simulates a basic login process using JavaScript.

---

## Product Requirements

The project must contain **one JavaScript file** that simulates a login process when executed in the browser console.

The JavaScript file must contain the main project logic using variables, conditionals, loops, and functions.

---

## Logical Requirements

### 1. Configuration

A valid username and password must be hardcoded inside the JavaScript file using `const`.

Example:

```javascript
const USUARIO_CORRECTO = "user";
````

The project implements this concept using constants for the correct credentials.

---

### 2. Data Input

The program must use `prompt()` to request:

* The username.
* The password.

Example:

```javascript
let usuarioIngresado = prompt("Ingrese su usuario:");
let passwordIngresada = prompt("Ingrese su contraseña:");
```

---

### 3. Attempt Management

The user has a maximum of **3 attempts** to enter the correct credentials.

A loop must be used to control the number of attempts.

The recommended structure is:

```javascript
while (...)
```

The program must continue requesting credentials while attempts are still available.

---

### 4. Credential Validation

The program must validate the username and password using strict equality:

```javascript
===
```

Both credentials must be correct to allow access.

Example:

```javascript
if (
    usuarioIngresado === USUARIO_CORRECTO &&
    passwordIngresada === PASSWORD_CORRECTA
) {
    // Successful login
}
```

#### Successful Login

If the username and password are correct:

* The login process must finish.
* A welcome message must be displayed in the console.

Example:

```text
¡Bienvenido al sistema!
```

#### Incorrect Credentials

If the credentials are incorrect but attempts remain:

* The program must inform the user.
* The number of the current attempt must be displayed.
* The program must request the credentials again.

Example:

```text
Datos incorrectos. Intento 2 de 3.
```

#### Account Lock

If all three attempts are unsuccessful:

* The login process must finish.
* A blocking message must be displayed in the console.

Example:

```text
Usuario bloqueado. Ha superado el número de intentos.
```

---

## 5. Encapsulation

The complete login logic must be contained inside a function.

The function can be declared using the traditional function syntax:

```javascript
function validarAcceso() {
    // Login logic
}
```

The function must be called at the end of the JavaScript file so that the program executes:

```javascript
validarAcceso();
```

---

## Program Flow

The general logic of the program is:

```text
START
  |
  v
Set correct username and password
  |
  v
Set maximum attempts to 3
  |
  v
Request username
  |
  v
Request password
  |
  v
Are the credentials correct?
  |
  +-------------------+
  |                   |
 YES                  NO
  |                   |
  v                   v
Welcome          Increase attempt
message                |
  |                   v
  |             Are attempts < 3?
  |                   |
  |              +----+----+
  |             YES        NO
  |              |          |
  |              v          v
  |           Try again   Block user
  |                         |
  +------------+------------+
               |
              END
```

---

## Technologies

* JavaScript
* Browser Console
* `const`
* `let`
* `prompt()`
* `while`
* `if / else`
* `===`
* `&&`
* `console.log()`
* Functions

---

## Expected Learning Outcomes

After completing the exercise, the student should be able to:

* Declare and use variables.
* Understand the difference between `const` and `let`.
* Capture user input using `prompt()`.
* Compare values using strict equality (`===`).
* Combine conditions using logical operators.
* Implement repetition using a `while` loop.
* Control the number of login attempts.
* Use `if / else` conditional structures.
* Encapsulate logic inside a function.
* Execute a function from the JavaScript file.
* Explain the program's logical flow.

---

## Expected Results

The program should:

1. Execute without errors in the browser console.
2. Request the username.
3. Request the password.
4. Validate the credentials correctly.
5. Allow a maximum of three attempts.
6. Display a welcome message when the credentials are correct.
7. Display an incorrect-credentials message when attempts remain.
8. Display a blocking message after three failed attempts.
9. Keep the complete login logic organized inside a function.

---

## Project Structure

```text
First-Time-JavaScript-Assessment/
│
├── README.md
│
└── login-corrected-003.js
```

---

## Execution

The JavaScript file can be executed directly from the browser console.

Example:

```javascript
validarAcceso();
```

The program will request the username and password through `prompt()` and display the corresponding result in the browser console.

---

## Assessment Status

**Momento 1:** Completed

Focus:

> Variables → Conditionals → Loops → Functions → Encapsulation

---

````

### A small Git recommendation

For this assessment, I'd keep your repository structure simple:

```text
First-Time-JavaScript-Assessment/
├── README.md
└── login-corrected-003.js
````

Then you can make a clean commit such as:

```bash
git add README.md login-corrected-003.js
git commit -m "feat: add JavaScript login assessment"
git push
```

That gives you a nice first milestone in Git history:

```text
Initial project
      │
      ▼
feat: add JavaScript login assessment
      │
      ├── README.md
      └── login-corrected-003.js
```

One thing I particularly like about structuring it this way for your assessment: **the README explains the reasoning behind the code, while the `.js` file remains clean and focused on the actual implementation.** That makes it much easier to explain in class when they ask you *"¿por qué utilizaste `while`?", "¿qué hace `===`?", "¿por qué `const`?",* or *"¿dónde está la encapsulación?"*.
