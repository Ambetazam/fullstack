let user_one;
let password_user_one;
let user_input;
let password_input;

let wrong = 2;

function attemps(){
	while ( wrong < 0 && user_one != user_input && password_user_one != password_input) {
		console.log(`Incorrect User or Password:\nPlease try again\n${wrong} attemps left!`);
		if (wrong === 0){
			console.log = (`Session blocked by too many failed attemps!\n`);
			alert(Your current session token has been loocked);
			break;
		}
		 wrong = wrong - wrong;
	}
}
