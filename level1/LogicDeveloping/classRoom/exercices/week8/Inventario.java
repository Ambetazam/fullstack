import java.util.Scanner;

public class Inventario{

	public static void main(String[] args) {

	// 1. Declaracion del scanner en el main 'it allows me to run the scanner and callit whetever place'.

	Scanner reader = new Scanner(System.in);
	System.out.println("Gracias por ingresar al Sistema de Inventarios de Galletas Noel Grupo Nutresa.");
	// 2. Declaracion de un array de 5 campos.
	String[] cookies = new String[5];
	cookies[0]= "Ducales";
	cookies[1]= "Festival";
	cookies[2]= "Tosh";

	int opciones = 0;


	while (opciones != 4){

		System.out.println("Por Favor Seleccione una opcion ingresando un numero del 1 al 5:");
		System.out.println("1. Listar Productos Disponibles.");
		System.out.println("2. Buscar Productos Disponibles.");
		System.out.println("3. Agregar Productos.");
		System.out.println("4. Salir.");

		opciones = reader.nextInt();
		reader.nextLine(); // Permite limpiar la memoria interna del scanner; "refresh".

		switch (opciones){

			case 1:
				System.out.println("\nProductos Disponibles:\n");

				for (String cookie : cookies){
					if (cookie != null){
						System.out.println("***" + cookie);
					}
				}

			break;


			case 2:

				System.out.println("Por favor escriba el nombre del producto que desea buscar:");
				String buscarProducto = reader.nextLine();

				boolean disponible = encontrarProducto(cookies, buscarProducto);

				if (disponible){
					System.out.println("\nProducto Disponible.\n");
				}else{
					System.out.println("\nEl Producto " + buscarProducto +  " solicitado no esta disponible.\n");
				}

			break;


			case 3:

				System.out.println("\nIngrese el nombre del nuevo producto:\n");
				String nuevoProducto = reader.nextLine();

				boolean productoAgregado = false;

				for (int i = 0; i < cookies.length; i++){
					if (cookies[i] == null){
						cookies[i] = nuevoProducto;
						productoAgregado = true;
						System.out.println("\nEl Producto: " + nuevoProducto + " Ha sido agregado al inventario.\n");
						break;
					}
				}

				if (!productoAgregado){
					System.out.println("\nNo se pueden agregar mas productos al inventario.\n");
				}
			break;

			case 4:
				System.out.println("\nGracias por usar nuestros servicios...\n");
				System.out.println("\nHasta pronto!\n");
			break;
		
			default:
				System.out.println("\nOpcion no permitida!\n");

		}
	}
	reader.close();
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
