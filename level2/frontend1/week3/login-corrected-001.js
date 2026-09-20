const user_one = 'normalUser';
const password_user_one = 'simple1234'; 
let initMessage = "Welcome to our system!\nPlease insert your user and password:\n"; 
let wrong = 2; 
let attempts = true; 

while (attempts) { 
	let user_input = prompt('Insert your User:\n');
	let password_input = prompt('Insert your Password:\n');
	if (user_one === user_input && password_user_one === password_input) { 
		console.log("Login successful!"); 
		console.log(`Welcome ${user_input}!`); 
		attempts = false; 
	} else { 
		wrong--; 
		if (wrong <= 0) { 
			console.log( "You have no attempts left to log in.\n" + "Your current session has been locked!" ); 
			attempts = false;
		 } else { 
			console.log( "Incorrect User or Password.\n" + "Please try again.\n" + `${wrong} attempts left!` );
		 }
	 } 
}
