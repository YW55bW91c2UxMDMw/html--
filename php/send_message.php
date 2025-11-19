<?php
// send_message.php : 새 메시지 저장

header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/db.php';

$username = trim($_POST['username'] ?? '');
$message  = trim($_POST['message'] ?? '');

if ($message === '') {
    echo json_encode(['ok' => false, 'error' => '메시지가 비어 있습니다.']);
    exit;
}

if ($username === '') {
    $username = '익명';
}

// 길이 제한 (너무 긴 스팸 방지)
if (mb_strlen($username, 'UTF-8') > 20) {
    $username = mb_substr($username, 0, 20, 'UTF-8');
}
if (mb_strlen($message, 'UTF-8') > 500) {
    $message = mb_substr($message, 0, 500, 'UTF-8');
}

try {
    $stmt = $pdo->prepare('INSERT INTO messages (username, message) VALUES (:u, :m)');
    $stmt->execute([
        ':u' => $username,
        ':m' => $message,
    ]);
    echo json_encode(['ok' => true]);
} catch (Exception $e) {
    echo json_encode(['ok' => false, 'error' => 'DB 오류']);
}
