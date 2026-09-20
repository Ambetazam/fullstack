const user_one = 'normalUser';
const password_user_one = 'simple1234';

let initMessage = "Wellcome to our system!\nPlease Insert your user and password:\n";
let user_input = prompt('Insert your User:\n');
let password_input = prompt('Insert your Password');

let wrong = 2;

attemps = true;

function attemps(user_one,password_user_one){
	while ( wrong < 0 && user_one != user_input || password_user_one != password_input) {
	wrong = wrong - wrong;
	};
};

function messages(wrong,attemps){
	if(wrong <= 0){

		console.log(`You have ${wrong} attemps to log in.\nYour current session has been loocked!`);
		//break;
	}else{
		console.log(`Incorrect User or Password:\nPlease try again\n${wrong} attemps left!`);
		break;
	};
}

while (attemps = false){};
