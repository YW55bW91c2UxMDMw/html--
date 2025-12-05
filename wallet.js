const SUPABASE_URL = 'https://podegnqsxajvtegplsvo.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvZGVnbnFzeGFqdnRlZ3Bsc3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MzgyMjMsImV4cCI6MjA3OTExNDIyM30.uq9VhsOyJYDtarKIDAxGnoq_K1BHCOp4DFp57rUSEL4';
window.client = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 공통 도메인 설정 (이걸로 통일!)
const EMAIL_DOMAIN = '@jindostar.net'; 

// ============================================================
// 2. 통합 인증 함수 (로그인 / 회원가입 / 로그아웃)
// ============================================================

// [로그인]
async function systemLogin(id, password) {
    if (!id || !password) return alert("아이디와 비밀번호를 입력하세요.");
    
    // 아이디만 입력해도 도메인 자동 완성
    const email = id.includes('@') ? id : id + EMAIL_DOMAIN;

    const { data, error } = await window.client.auth.signInWithPassword({
        email: email,
        password: password
    });

    if (error) {
        if(error.message.includes("Invalid login credentials")) {
            alert("로그인 실패: 아이디 또는 비밀번호가 틀렸습니다.");
        } else {
            alert("오류 발생: " + error.message);
        }
        return false;
    } else {
        // alert("로그인 성공!"); // (선택사항)
        location.reload(); // 새로고침하여 상태 반영
        return true;
    }
}

// [회원가입]
async function systemRegister(id, password) {
    if (!id || !password) return alert("아이디와 비밀번호를 입력하세요.");
    
    // 유효성 검사 (영문, 숫자, 언더바만 허용)
    const idRegex = /^[a-z0-9_]+$/;
    if (!idRegex.test(id)) return alert("아이디는 영문 소문자, 숫자, 언더바(_)만 가능합니다.");
    if (password.length < 6) return alert("비밀번호는 6자리 이상이어야 합니다.");

    const email = id + EMAIL_DOMAIN;

    // 1. 가입 시도
    const { data, error } = await window.client.auth.signUp({
        email: email,
        password: password
    });

    if (error) {
        alert("가입 실패: " + error.message);
        return false;
    }

    // 2. 프로필 생성 (지갑 초기화)
    if (data.user) {
        const { error: profileError } = await window.client
            .from('profiles')
            .upsert({ 
                id: data.user.id, 
                username: id, 
                nickname: id, 
                money: 100000, 
                token: 0,
                stardust: 0 
            });
        
        if (profileError) console.error("프로필 생성 오류:", profileError);

        alert(`환영합니다! [${id}] 계정이 생성되었습니다.\n자동으로 로그인됩니다.`);
        location.reload();
        return true;
    }
}

// [로그아웃]
async function systemLogout() {
    if (confirm("정말 로그아웃 하시겠습니까?")) {
        await window.client.auth.signOut();
        location.href = 'index.html'; // 메인으로 이동
    }
}

// ============================================================
// 3. 지갑 및 유저 정보 관리
// ============================================================
let myWallet = { money: 0, token: 0, stardust: 0 };

async function loadWallet() {
    const { data: { user } } = await window.client.auth.getUser();

    if (!user) {
        console.log("비로그인 상태");
        updateAuthUI(null); // UI를 비로그인 상태로 변경
        return;
    }

    // 로그인 상태라면 프로필 가져오기
    updateAuthUI(user); 

    const { data, error } = await window.client
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();

    if (data) {
        myWallet = data;
        updateGlobalUI(); // 지갑 숫자 갱신
    }
}

// 상단 로그인/로그아웃 버튼 UI 변경 (모든 페이지 공통)
function updateAuthUI(user) {
    const ui = document.getElementById('auth-ui');
    if (!ui) return; // 해당 UI가 없는 페이지는 패스

    if (user) {
        // 로그인 상태일 때
        ui.innerHTML = `
            <span style="color:#aaa; font-size:0.8rem; margin-right:10px;"> 접속중</span>
            <a href="mypage.html" class="auth-btn">마이페이지</a>
            <button onclick="systemLogout()" class="auth-btn primary" style="background:#333;">로그아웃</button>
        `;
        
        // 관리자 버튼 추가 체크 (비동기)
        window.client.from('profiles').select('is_admin').eq('id', user.id).single()
            .then(({ data }) => {
                if (data && data.is_admin) {
                    const btn = document.createElement('a');
                    btn.href = 'admin.html';
                    btn.className = 'auth-btn admin';
                    btn.innerText = 'ADMIN';
                    btn.style.marginRight = '5px';
                    ui.prepend(btn);
                }
            });

    } else {
        // 비로그인 상태일 때
        ui.innerHTML = `
            <button onclick="openAuthModal()" class="auth-btn primary">로그인 / 가입</button>
        `;
    }
}

function updateGlobalUI() {
    // 각 페이지에 있는 요소 ID가 있으면 업데이트
    const els = {
        money: ['global-money', 'money', 'my-money'],
        token: ['global-token', 'token', 'my-token'],
        stardust: ['my-stardust', 'ui-stardust']
    };

    els.money.forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = myWallet.money.toLocaleString();
    });
    els.token.forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = myWallet.token.toLocaleString();
    });
    els.stardust.forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = (myWallet.stardust || 0).toLocaleString();
    });
}

// 페이지 로드 시 자동 실행
window.onload = function() {
    loadWallet();
    
    // 만약 페이지별 추가 초기화 함수가 있다면 실행
    if (typeof initPage === 'function') initPage();
};