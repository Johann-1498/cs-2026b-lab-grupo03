// A3 (versión inicial): ninguna mención de implementación en la respuesta.
// Auto-contenida (sin require): el mismo código se puede pegar inline en casos.yaml.
const PROHIBIDAS = ['postgresql', 'django', 'react', 'endpoint', 'tabla', 'api de', 'base de datos'];
module.exports = (output) => {
  const texto = String(output).toLowerCase();
  const hallada = PROHIBIDAS.find((p) => texto.includes(p));
  return { pass: !hallada, score: hallada ? 0 : 1, reason: hallada ? `Menciona: ${hallada}` : 'Sin detalles de implementación' };
};
