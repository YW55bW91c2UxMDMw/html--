<?php
// load_messages.php : 새로운 메시지 목록을 JSON으로 반환

header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/db.php';

$afterId = isset($_GET['after_id']) ? (int)$_GET['after_id'] : 0;

if ($afterId > 0) {
    $stmt = $pdo->prepare(
        'SELECT id, username, message,
                DATE_FORMAT(created_at, "%H:%i:%s") AS time
         FROM messages
         WHERE id > :id
         ORDER BY id ASC'
    );
    $stmt->execute([':id' => $afterId]);
} else {
    // 맨 처음 접속했을 때는 최근 50개만
    $stmt = $pdo->query(
        'SELECT id, username, message,
                DATE_FORMAT(created_at, "%H:%i:%s") AS time
         FROM messages
         ORDER BY id DESC
         LIMIT 50'
    );
    $rows = $stmt->fetchAll();
    // 최근 것이 위에 오니까, 시간 순서를 맞추기 위해 뒤집기
    $rows = array_reverse($rows);
    
    echo json_encode(['ok' => true, 'messages' => $rows]);
    exit;
}

$rows = $stmt->fetchAll();
echo json_encode(['ok' => true, 'messages' => $rows]);
