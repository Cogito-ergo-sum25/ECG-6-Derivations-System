// Definimos los pines ADC que usaremos.
// GPIO34 y GPIO35 son excelentes opciones porque son solo de entrada.
const int PIN_DERIVACION_I = 34;
const int PIN_DERIVACION_II = 14;

void setup() {
  // Inicializamos la comunicación serial. 115200 es una velocidad rápida y confiable.
  // Esta velocidad debe coincidir con la del script de Python en tu computadora.
  Serial.begin(115200);

  // Mensaje de inicio para saber que el ESP32 ha arrancado correctamente.
  // Lo verás si abres el "Monitor Serie" del Arduino IDE.
  Serial.println("Iniciando lectura de ECG (Derivaciones I y II)...");
}

void loop() {
  // Leemos el valor analógico de cada pin.
  // El ADC del ESP32 tiene una resolución de 12 bits, por lo que el valor irá de 0 a 4095.
  int valor_I = analogRead(PIN_DERIVACION_I);
  int valor_II = analogRead(PIN_DERIVACION_II);

  // Enviamos los datos a la computadora por el puerto serie.
  // El formato es clave: "valor1,valor2" seguido de un salto de línea.
  Serial.print(valor_I);
  Serial.print(",");
  Serial.println(valor_II);

  delay(3);
}