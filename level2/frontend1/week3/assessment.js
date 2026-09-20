let user_one;
let password_user_one;
let user_input;
let password_input;

let wrong = 2;

function intentos(){
	while ( wrong < 0 && user_one != user_input && password_user_one != password_input) {
		 alert('Your current session token has been loocked');
		 console.log = ('Session blocked by too many failed tries');
		 wrong = wrong - wrong;
	}
}
