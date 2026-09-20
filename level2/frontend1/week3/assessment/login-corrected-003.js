const USUARIO_CORRECTO = "normalUser"; 
const PASSWORD_CORRECTA = "simple1234"; 

function validarAcceso() { 
	let intentos = 3;
	
	while (intentos > 0) { 
		let usuarioIngresado = prompt("Ingrese su usuario:"); 
		let passwordIngresada = prompt("Ingrese su contraseña:"); 
		
		if ( usuarioIngresado === USUARIO_CORRECTO && passwordIngresada === PASSWORD_CORRECTA ) { 
			console.log("¡Bienvenido al sistema!"); 
			break;
		 } else { 
			intentos--; 

			if (intentos > 0) { 
				console.log( `Datos incorrectos. Intento ${3 - intentos} de 3.` ); 
			} else { 
				console.log( "Usuario bloqueado. Ha superado el número de intentos." );
			} 
		} 
	} 
}
 validarAcceso();
