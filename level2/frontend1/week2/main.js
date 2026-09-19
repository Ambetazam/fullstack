/***
let age = 10;
let age2 = 15;
let hasEntry = true;

alert(`The age is ${age} years old`)

let answer_one = age > age2;
console.log(answer_one);

answer_two = age < age2 || age === age2;// triple = sign to make compare if it is equals
console.log(answer_two);
***/
// votation system

const MIN_AGE = 18;
const NATIONALITY = "Colombia"; //I changed to 'colombia' to change the user input to lower case.

let userAge;
let userNationality;


userNationality = prompt("Input your age: ");
userAge = parseInt(prompt("Input your country: "));


let answer = userAge >= MIN_AGE && userNationality === NATIONALITY;
console.log(`You can vote: ${answer}`);

let other_answer = MIN_AGE > userAge || NATIONALITY != userNationality;
console.log(`Youn can vote: ${other_answer} `);

/***
if(userAge >= MIN_AGE){
  userNationality = prompt(`What's your nationality?: `);
  if(userNationality === NATIONALITY){
    console.log(`You can vote`);
  } else {
    let citizen = prompt(`You'r Colombian`);
    if(citizen === 'yes'){
      console.log(`You can vote`);
    } else {
      console.log(`You can't vote`);
    }

}

***/














