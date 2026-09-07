import java.util.Scanner;

public class Inventario{

	public static void main(String[] args) {

	// 1. Declaracion del scanner en el main 'it allows me to run the scanner and callit whetever place'.

	Scanner reader = new Scanner(System.in);
	
	// 2. Declaracion de un array de 5 campos.
	String[] cookies = new String[4];
	cookies[0]= "Ducales";
	cookies[1]= "Festival";
	cookies[2]= "Tosh";
	cookies[3]= null;
	cookies[4]= null;
	
	int opciones = 0;


	// Ciclo for: para agregar los campos en null
	for(int i = 2; i < cookies.length; i++){

	}

	// Ciclo while para listar opciones con menu en switch


	while (opciones != 4){

		System.out.println("\nGracias Por Usar Nuestro Sistema de Invetarios\n");
		System.out.println("\nCordial Saludo;\n");
		System.out.println("\n\nPor Favor Seleccione una opcion ingresando un numero del 1 al 5:\n\n");
		System.out.println("\n1. Listar Productos Disponibles.\n");
		System.out.println("\n2. Buscar Productos Disponibles. \n");
		System.out.println("\n3. Agregar Productos.\n");
		System.out.println("\n4. Salir.\n");
		System.out.println("\n\nPor Favor Seleccione una opcion ingresando un numero del 1 al 5:\n\n");

		opciones = reader.nextInt();
		reader.nextLine(); // Permite limpiar la memoria interna del scanner; "refresh".

		switch (opciones){
		
			case 1:
				System.out.println("\nProductos Disponibles:\n");

				for (cookie : cookies){
					if (cookie != null){
						System.out.println("\n" + cookie);
					}
				}

				break;


			case 2:

				System.out.println("\nPor favor escriba el nombre del producto que desea buscar:\n");
				String buscarProducto = reader.nextline();
				boolean disponible = encontrarProducto(cookies, buscarProducto);
				if (disponible){
					System.out.println("\nProducto Disponible.\n");
				}else{
					System.out.println("\nEl Producto solicitado no esta disponible.\n");
				}
				break;


			case 3:

			case 4:

			default:
				System.out.println("\nOpcion no permitida!\n");



		}

	reader.close();


	}





	}

	// Funcion para buscar el producto:

	public static boolean encontrarProducto(String[] cookies, String buscarProducto){

		for (String cookie : cookies){
			if (cookie != null && cookie.equalsIgnoreCase(buscarProducto)){
				return true;
			}
		}

		return false;
	}

}
