let names = ['Vero','Estefa','Me'];

let numbers = [1,2,3,4,5];


/***let pairNumbers = numbers.map((number) => {
  if (number % 2 === 0) {
    return number;
  }
});
***/

let pairNumbers = numbers.filter((number) => {
  return number % 2 === 0;
})


console.log(pairNumbers);

/***
let editedNames = names.map((any) => {
  return any + "Students";
});


let number = 2


if (number%2 === 0) {
  return number

}
***/
