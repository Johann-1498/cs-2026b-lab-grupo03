// A3: los ESCENARIOS describen comportamiento observable, no la implementación.
// Se revisan solo los escenarios (no las preguntas al Product Owner): una pregunta
// como "¿qué necesidad se ve afectada por la base de datos?" es correcta.
// Versión 2 de la aserción: "tabla" solo cuenta en sentido de base de datos
// (la tabla que el usuario VE en pantalla es comportamiento observable).
// Auto-contenida (sin require): el mismo código se puede pegar inline en casos.yaml.
const parsear = (o) => { try { const x = JSON.parse(o); return x && typeof x === 'object' && !Array.isArray(x) ? x : null; } catch (e) { return null; } };
const ok = (pass, reason) => ({ pass, score: pass ? 1 : 0, reason });
const PROHIBIDAS = [
  /\bpostgres(ql)?\b/, /\bdjango\b/, /\breact\b/, /\bjwt\b/, /\bendpoints?\b/,
  /\bapis?\b/, /\bbase de datos\b/, /\bsql\b/, /\borm\b/,
  /\btablas? (de la |de )?(base|bd)\b/,
];
module.exports = (output) => {
  const r = parsear(output);
  const texto = (r ? JSON.stringify(r.escenarios || []) : String(output)).toLowerCase();
  const hallada = PROHIBIDAS.find((p) => p.test(texto));
  return ok(!hallada, hallada ? `Menciona implementación: ${hallada}` : 'Sin detalles de implementación');
};
