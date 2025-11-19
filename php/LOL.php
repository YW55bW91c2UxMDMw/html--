<?php
const DB_HOST = 'sql311.infinityfree.com';
const DB_NAME = 'if0_40438494_chat';
const DB_USER = 'if0_40438494';
const DB_PASS = 'orvELJY9ZR';
function get_pdo() {
    static $pdo = null;
    if ($pdo === null) {
        $dsn = 'mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset=utf8mb4';
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ];
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
    }
    return $pdo;
}

// ====== 2. API 처리 (JSON) ======
$action = $_GET['action'] ?? $_POST['action'] ?? null;

if ($action === 'send') {
    header('Content-Type: application/json; charset=utf-8');
    $username = trim($_POST['username'] ?? '');
    $message  = trim($_POST['message'] ?? '');

    if ($message === '') {
        echo json_encode(['ok' => false, 'error' => '메시지가 비어 있습니다.']);
        exit;
    }

    if ($username === '') {
        $username = '익명';
    }

    // 길이 제한
    if (mb_strlen($username, 'UTF-8') > 20) {
        $username = mb_substr($username, 0, 20, 'UTF-8');
    }
    if (mb_strlen($message, 'UTF-8') > 500) {
        $message = mb_substr($message, 0, 500, 'UTF-8');
    }

    try {
        $pdo = get_pdo();
        $stmt = $pdo->prepare('INSERT INTO messages (username, message) VALUES (:u, :m)');
        $stmt->execute([
            ':u' => $username,
            ':m' => $message,
        ]);
        echo json_encode(['ok' => true]);
    } catch (Exception $e) {
        echo json_encode(['ok' => false, 'error' => 'DB 오류']);
    }
    exit;
}

if ($action === 'load') {
    header('Content-Type: application/json; charset=utf-8');
    $afterId = isset($_GET['after_id']) ? (int)$_GET['after_id'] : 0;

    try {
        $pdo = get_pdo();
        if ($afterId > 0) {
            $stmt = $pdo->prepare(
                'SELECT id, username, message,
                        DATE_FORMAT(created_at, "%H:%i:%s") AS time
                 FROM messages
                 WHERE id > :id
                 ORDER BY id ASC'
            );
            $stmt->execute([':id' => $afterId]);
            $rows = $stmt->fetchAll();
        } else {
            // 첫 로딩: 최근 50개만
            $stmt = $pdo->query(
                'SELECT id, username, message,
                        DATE_FORMAT(created_at, "%H:%i:%s") AS time
                 FROM messages
                 ORDER BY id DESC
                 LIMIT 50'
            );
            $rows = $stmt->fetchAll();
            $rows = array_reverse($rows); // 시간순 정렬
        }
        echo json_encode(['ok' => true, 'messages' => $rows]);
    } catch (Exception $e) {
        echo json_encode(['ok' => false, 'error' => 'DB 오류']);
    }
    exit;
}

?>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>spin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
        :root {
            --bg-main: #050510;
            --bg-card: #101020;
            --bg-input: #151528;
            --accent: #ff4f6d;
            --accent-soft: rgba(255, 79, 109, 0.15);
            --text-main: #f5f5f5;
            --text-muted: #a4a4c5;
            --border-soft: #262648;
        }
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top, #201840 0, #050510 55%, #020208 100%);
            color: var(--text-main);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 16px;
        }
        #chat-shell {
            width: 100%;
            max-width: 680px;
            height: 80vh;
            max-height: 720px;
            background: linear-gradient(145deg, rgba(255,255,255,0.02), rgba(0,0,0,0.7));
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            box-shadow:
                0 18px 40px rgba(0,0,0,0.6),
                0 0 0 1px rgba(255,255,255,0.03);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }
        #chat-header {
            padding: 14px 18px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            background: radial-gradient(circle at top left, rgba(255,79,109,0.15), transparent 55%);
        }
        #chat-header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        #chat-title {
            font-weight: 600;
            font-size: 1rem;
        }
        #chat-subtitle {
            font-size: 0.78rem;
            color: var(--text-muted);
        }
        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #35d48b;
            box-shadow: 0 0 8px #35d48b;
        }
        #chat-header-right {
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        #message-list {
            flex: 1;
            padding: 14px 18px;
            overflow-y: auto;
            background: radial-gradient(circle at top right, rgba(255,79,109,0.06), transparent 55%);
        }
        .message-item {
            margin-bottom: 10px;
            padding: 8px 10px;
            border-radius: 10px;
            border: 1px solid var(--border-soft);
            background: rgba(7, 7, 18, 0.96);
            box-shadow: 0 4px 10px rgba(0,0,0,0.45);
            max-width: 80%;
            word-wrap: break-word;
        }
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 3px;
        }
        .message-username {
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--accent);
        }
        .message-time {
            font-size: 0.7rem;
            color: var(--text-muted);
        }
        .message-body {
            font-size: 0.86rem;
            color: var(--text-main);
        }
        #input-area {
            padding: 10px 10px 12px;
            border-top: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(180deg, rgba(5,5,18,0.85), rgba(2,2,8,0.95));
            display: flex;
            flex-direction: column;
            gap: 7px;
        }
        #top-input-row {
            display: flex;
            gap: 8px;
        }
        #username-input {
            width: 110px;
            padding: 7px 9px;
            border-radius: 999px;
            border: 1px solid var(--border-soft);
            background: var(--bg-input);
            color: var(--text-main);
            font-size: 0.8rem;
            outline: none;
        }
        #username-input::placeholder {
            color: var(--text-muted);
        }
        #message-input-row {
            display: flex;
            gap: 8px;
        }
        #message-input {
            flex: 1;
            padding: 9px 11px;
            border-radius: 999px;
            border: 1px solid var(--border-soft);
            background: var(--bg-input);
            color: var(--text-main);
            font-size: 0.86rem;
            outline: none;
        }
        #message-input::placeholder {
            color: var(--text-muted);
        }
        #send-button {
            padding: 0 16px;
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg, var(--accent), #ff8b4f);
            color: #fff;
            font-weight: 600;
            font-size: 0.86rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            box-shadow: 0 6px 14px rgba(255,79,109,0.45);
            transition: transform 0.06s ease, box-shadow 0.06s ease, filter 0.06s ease;
        }
        #send-button:hover {
            filter: brightness(1.05);
            box-shadow: 0 8px 18px rgba(255,79,109,0.6);
        }
        #send-button:active {
            transform: translateY(1px);
            box-shadow: 0 3px 8px rgba(255,79,109,0.4);
        }
        #footer-note {
            text-align: right;
            font-size: 0.7rem;
            color: var(--text-muted);
            padding: 0 14px 4px;
        }

        /* 스크롤바 살짝 커스터마이징 */
        #message-list::-webkit-scrollbar {
            width: 6px;
        }
        #message-list::-webkit-scrollbar-track {
            background: transparent;
        }
        #message-list::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.12);
            border-radius: 999px;
        }

        /* 작은 화면 대응 */
        @media (max-width: 480px) {
            #chat-shell {
                height: 85vh;
                max-height: none;
            }
            #username-input {
                width: 90px;
            }
        }
        .sausage {
    position: fixed;          /* 화면에 고정 */
    top: 50%;                 /* 세로 가운데 */
    width: 350px;              /* 필요하면 크기 조절 */
    height: auto;
    transform-origin: center center;
    z-index: 5;               /* 채팅 박스보다 위에 오도록 */
    pointer-events: none;     /* 클릭 막기 (채팅 클릭 방해 안 되게) */
}

/* 왼쪽 소시지 */
.sausage-left {
    left: 10px;
    animation: spin-left 1s linear infinite;
}

/* 오른쪽 소시지 */
.sausage-right {
    right: 10px;
    animation: spin-right 1s linear infinite;
}

/* 시계방향 회전 */
@keyframes spin-left {
    from { transform: translateY(-50%) rotate(0deg); }
    to   { transform: translateY(-50%) rotate(360deg); }
}

/* 반시계 방향 회전 */
@keyframes spin-right {
    from { transform: translateY(-50%) rotate(0deg); }
    to   { transform: translateY(-50%) rotate(-360deg); }
}

/* 작은 화면에서는 조금 줄이기 (선택사항) */
@media (max-width: 480px) {
    .sausage {
        width: 55px;
    }
    .sausage-left {
        left: 4px;
    }
    .sausage-right {
        right: 4px;
    }
}
    </style>
</head>
<body>
    <img src="sausage.jpg" alt="sausage" class="sausage sausage-left">
    <img src="sausage.jpg" alt="sausage" class="sausage sausage-right">
    <div id="chat-shell">
        <div id="chat-header">
            <div id="chat-header-left">
                <div class="status-dot"></div>
                <div>
                    <div id="chat-title">익명 채팅</div>
                    <div id="chat-subtitle">익명으로 잠깐 쉬어가는 채팅방</div>
                </div>
            </div>
            <div id="chat-header-right">
                실시간 연결 · <span id="user-count">∞</span> online
            </div>
        </div>

        <div id="message-list"></div>

        <div id="input-area">
            <div id="top-input-row">
                <input type="text" id="username-input" value="익명" placeholder="닉네임 (비워두면 익명)">
            </div>
            <div id="message-input-row">
                <input type="text" id="message-input" placeholder="메시지를 입력하고 Enter 또는 전송 버튼을 눌러주세요">
                <button id="send-button">
                    <span>전송</span>
                </button>
            </div>
            <div id="footer-note">
                저장은 서버 DB에만 됩니다. 새로고침하면 최근 메시지만 다시 불러옵니다.
            </div>
        </div>
    </div>
    <audio autoplay loop>
      <source src="spin.mp3" type="audio/mpeg">
    </audio>

    <script>
        const messageList   = document.getElementById('message-list');
        const usernameInput = document.getElementById('username-input');
        const messageInput  = document.getElementById('message-input');
        const sendButton    = document.getElementById('send-button');

        let lastId = 0;

        function appendMessage(m) {
            const item = document.createElement('div');
            item.className = 'message-item';

            const header = document.createElement('div');
            header.className = 'message-header';

            const userSpan = document.createElement('span');
            userSpan.className = 'message-username';
            userSpan.textContent = m.username;

            const timeSpan = document.createElement('span');
            timeSpan.className = 'message-time';
            timeSpan.textContent = m.time || '';

            header.appendChild(userSpan);
            header.appendChild(timeSpan);

            const body = document.createElement('div');
            body.className = 'message-body';
            body.textContent = m.message;

            item.appendChild(header);
            item.appendChild(body);

            messageList.appendChild(item);
            messageList.scrollTop = messageList.scrollHeight;
        }

        async function loadMessages(initial = false) {
            try {
                const url = new URL(window.location.href);
                url.searchParams.set('action', 'load');
                if (!initial && lastId > 0) {
                    url.searchParams.set('after_id', lastId);
                } else {
                    url.searchParams.delete('after_id');
                }

                const res = await fetch(url.toString(), {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                const data = await res.json();
                if (!data.ok) return;

                data.messages.forEach(m => {
                    appendMessage(m);
                    lastId = m.id;
                });
            } catch (e) {
                console.error('loadMessages error:', e);
            }
        }

        async function sendMessage() {
            const username = usernameInput.value.trim();
            const message  = messageInput.value.trim();
            if (message === '') return;

            const formData = new FormData();
            formData.append('action', 'send');
            formData.append('username', username);
            formData.append('message',  message);

            try {
                const res = await fetch(window.location.pathname, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (!data.ok) {
                    alert('전송 실패: ' + (data.error || '알 수 없는 오류'));
                    return;
                }
                messageInput.value = '';
                await loadMessages(false);
            } catch (e) {
                console.error('sendMessage error:', e);
                alert('전송 중 오류가 발생했습니다.');
            }
        }

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });

        // 처음 로딩 시 최근 메시지 50개
        loadMessages(true);
        // 2초마다 신규 메시지 확인
        setInterval(() => loadMessages(false), 2000);
    </script>
</body>
</html>