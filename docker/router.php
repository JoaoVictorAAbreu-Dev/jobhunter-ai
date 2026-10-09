<?php
declare(strict_types=1);

// Roteador local para a API PHP e o frontend estático.
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH);
if (!is_string($path)) {
    http_response_code(400);
    exit('Requisição inválida');
}
if ($path === '/api/vagas' || $path === '/api/vagas.php') {
    require dirname(__DIR__) . '/php/api/vagas.php';
    return true;
}
if ($path === '/') {
    $path = '/index.html';
}
$root = realpath(dirname(__DIR__) . '/site');
$file = realpath(dirname(__DIR__) . '/site' . $path);
if ($root !== false && $file !== false && str_starts_with($file, $root . DIRECTORY_SEPARATOR) && is_file($file)) {
    return false;
}
http_response_code(404);
header('Content-Type: text/plain; charset=utf-8');
echo 'Página não encontrada';
