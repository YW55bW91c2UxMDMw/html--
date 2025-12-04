const SUPABASE_URL = 'https://podegnqsxajvtegplsvo.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBvZGVnbnFzeGFqdnRlZ3Bsc3ZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM1MzgyMjMsImV4cCI6MjA3OTExNDIyM30.uq9VhsOyJYDtarKIDAxGnoq_K1BHCOp4DFp57rUSEL4';
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 내 지갑 정보 담을 변수
let myWallet = { money: 0, token: 0 };

// 2. 로그인 체크 및 지갑 불러오기
async function loadWallet() {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        // 비로그인 상태면 로그인 페이지로 보내거나 알림
        console.log("로그인이 필요합니다.");
        return;
    }

    // DB에서 내 돈 조회
    let { data, error } = await supabase
        .from('profiles')
        .select('money, token')
        .eq('id', user.id)
        .single();

    if (data) {
        myWallet = data;
        updateGlobalUI(); // 상단바 갱신
    } else {
        // 프로필이 없으면 새로 생성 (가입 초기)
        await supabase.from('profiles').insert({ id: user.id });
        myWallet = { money: 100000, token: 0 };
        updateGlobalUI();
    }
}

// 3. UI 갱신 함수
function updateGlobalUI() {
    const moneyEl = document.getElementById('global-money');
    const tokenEl = document.getElementById('global-token');
    
    // 게임 화면 UI도 있으면 같이 갱신
    const gameMoney = document.getElementById('money');
    const gameToken = document.getElementById('token');

    if (moneyEl) moneyEl.innerText = myWallet.money.toLocaleString();
    if (tokenEl) tokenEl.innerText = myWallet.token.toLocaleString();
    if (gameMoney) gameMoney.innerText = myWallet.money.toLocaleString();
    if (gameToken) gameToken.innerText = myWallet.token.toLocaleString();
}

// 4. (핵심) 돈/토큰 안전하게 변경하기 (RPC 호출)
async function updateBalance(type, amount) {
    let rpcName = '';
    
    if (type === 'money') rpcName = 'update_money'; // 아까 만든 SQL 함수
    if (type === 'token') rpcName = 'update_token';

    const { error } = await supabase.rpc(rpcName, { amount: amount });

    if (!error) {
        await loadWallet(); // DB 변경 후 최신값 다시 가져오기
        return true;
    } else {
        console.error("잔액 변경 실패:", error);
        return false;
    }
}

// 5. 환전 함수 (RPC 호출)
async function buyTokenDB(count) {
    const { error } = await supabase.rpc('exchange_token', { count: count });
    
    if (error) {
        alert("잔액이 부족하거나 오류가 발생했습니다.");
    } else {
        alert(`토큰 ${count}개 구매 완료!`);
        await loadWallet();
    }
}

// 페이지 열리면 실행
window.onload = function() {
    loadWallet();
};