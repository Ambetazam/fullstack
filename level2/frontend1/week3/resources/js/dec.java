import java.util.Base64;
import java.nio.charset.StandardCharsets;

String base64Str = "U2FsdSBDb3JyZWN0bw==";
byte[] decodedBytes = Base64.getDecoder().decode(base64Str);
String utf8Str = new String(decodedBytes, StandardCharsets.UTF_8);
System.out.println(utf8Str);

