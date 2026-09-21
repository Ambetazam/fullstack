const user_one = 'normalUser';
const password_user_one = 'simple1234';

let init = "Wellcome to our system!\nPlease Insert your user and password inside the next boxes:\n";
let user_input = prompt(`Hi and ${init}\n Insert your User:\n`);
let password_input = prompt('Insert your Password:');

let wrong = 2;



function attempts(user_one,password_user_one){
	while ( wrong < 0 && user_one != user_input || password_user_one != password_input) {
	wrong = wrong - wrong;
	};
};

function messages(wrong,attempts()){
	if(wrong >= 0){

		console.log(`You have ${wrong} attempts to log in.\nYour current session has been loocked!`);
		//break;
	}else{
		console.log(`Incorrect User or Password:\nPlease try again\n${wrong} attempts left!`);
		//break;
	};
}



attempts();
