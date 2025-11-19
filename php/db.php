<?php
// db.php : MySQL 연결 공통 파일

$DB_HOST = 'sql311.infinityfree.com';   // InfinityFree에서 본 host로 변경
$DB_NAME = 'if0_40438494_chat';      // 네 DB 이름
$DB_USER = 'if0_40438494';             // DB 사용자 이름
$DB_PASS = 'orvELJY9ZR';                  // DB 비밀번호

$dsn = "mysql:host=$DB_HOST;dbname=$DB_NAME;charset=utf8mb4";

$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
];

try {
    $pdo = new PDO($dsn, $DB_USER, $DB_PASS, $options);
} catch (PDOException $e) {
    http_response_code(500);
    echo "DB 연결 오류";
    // 개발 중에는 에러를 보고 싶으면 아래 주석을 잠깐 풀어도 됨
    // echo $e->getMessage();
    exit;
}
