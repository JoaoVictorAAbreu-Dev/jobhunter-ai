<?php
declare(strict_types=1);

/**
 * JobHunter AI — API PHP opcional.
 * Execute na raiz do repositório: php -S localhost:8000 -t .
 * GET /php/api/vagas.php?q=python&nivel=junior&modalidade=remoto&pagina=1&limite=12
 * Lê exclusivamente dados públicos gerados pelo coletor Python.
 */
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: public, max-age=60');
header('X-Content-Type-Options: nosniff');

function respond(int $status, array $payload): never {
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_INVALID_UTF8_SUBSTITUTE);
    exit;
}
function param(string $name, int $max = 100): string {
    $value = $_GET[$name] ?? '';
    if (!is_string($value)) respond(400, ['erro' => "Parâmetro inválido: $name"]);
    $value = trim($value);
    if (strlen($value) > $max) respond(400, ['erro' => "Parâmetro muito longo: $name"]);
    return $value;
}
function lower(string $text): string {
    return function_exists('mb_strtolower') ? mb_strtolower($text, 'UTF-8') : strtolower($text);
}
function matches(string $haystack, string $needle): bool {
    return $needle === '' || str_contains(lower($haystack), lower($needle));
}

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
    header('Allow: GET');
    respond(405, ['erro' => 'Método não permitido']);
}

$q = param('q');
$nivel = param('nivel', 40);
$area = param('area', 80);
$modalidade = param('modalidade', 80);
$local = param('local', 120);
$empresa = param('empresa', 120);
$ordem = param('ordem', 20) ?: 'pontuacao';
if (!in_array($ordem, ['pontuacao', 'empresa', 'titulo'], true)) {
    respond(400, ['erro' => 'Ordenação inválida']);
}
$pagina = filter_var($_GET['pagina'] ?? 1, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 100000]]);
$limite = filter_var($_GET['limite'] ?? 12, FILTER_VALIDATE_INT, ['options' => ['min_range' => 1, 'max_range' => 100]]);
if ($pagina === false || $limite === false) respond(400, ['erro' => 'Paginação inválida']);

$path = dirname(__DIR__, 2) . '/site/vagas.json';
if (!is_file($path) || !is_readable($path)) {
    respond(503, ['erro' => 'Dados indisponíveis. Execute o coletor Python e scripts/build_site.py antes de consultar.']);
}
try {
    $jobs = json_decode((string) file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
} catch (JsonException $e) {
    respond(503, ['erro' => 'Arquivo de vagas inválido']);
}
if (!is_array($jobs) || !array_is_list($jobs)) respond(503, ['erro' => 'Formato de vagas inválido']);

$filtered = array_values(array_filter($jobs, static function ($job) use ($q, $nivel, $area, $modalidade, $local, $empresa): bool {
    if (!is_array($job)) return false;
    $get = static fn(string $field): string => is_scalar($job[$field] ?? null) ? (string) $job[$field] : '';
    return matches(implode(' ', [$get('titulo'), $get('empresa'), $get('local'), $get('area'), $get('modalidade')]), $q)
        && matches($get('nivel'), $nivel)
        && matches($get('area'), $area)
        && matches($get('modalidade'), $modalidade)
        && matches($get('local'), $local)
        && matches($get('empresa'), $empresa);
}));
usort($filtered, static function ($a, $b) use ($ordem): int {
    if ($ordem === 'pontuacao') return ((float) ($b['pontuacao'] ?? 0)) <=> ((float) ($a['pontuacao'] ?? 0));
    return strnatcasecmp((string) ($a[$ordem] ?? ''), (string) ($b[$ordem] ?? ''));
});
$total = count($filtered);
respond(200, [
    'total' => $total,
    'pagina' => $pagina,
    'limite' => $limite,
    'paginas' => (int) ceil($total / $limite),
    'vagas' => array_slice($filtered, ($pagina - 1) * $limite, $limite),
]);
