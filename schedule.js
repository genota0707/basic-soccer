// 日程・空き枠は data/schedule.json から表示します。編集用シートから定期同期します。
(async () => {
    const eventContainer = document.getElementById('event-schedule-container');
    const bookingContainer = document.getElementById('personal-schedule-container');
    const lineUrl = 'https://lin.ee/yodgItoA';
    const dateLabel = (iso) => new Intl.DateTimeFormat('ja-JP', {
        timeZone: 'Asia/Tokyo', month: 'long', day: 'numeric', weekday: 'short'
    }).format(new Date(`${iso}T12:00:00+09:00`));
    const todayParts = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(new Date());
    const part = (name) => todayParts.find(item => item.type === name).value;
    const today = `${part('year')}-${part('month')}-${part('day')}`;
    const label = (tag, value, css) => {
        const node = document.createElement(tag);
        node.className = css;
        node.textContent = value;
        return node;
    };
    const message = (container, value) => {
        if (container) container.append(label('p', value, 'text-slate-400 text-sm'));
    };

    try {
        const response = await fetch('data/schedule.json', {cache: 'no-store'});
        if (!response.ok) throw new Error(`Schedule request failed: ${response.status}`);
        const data = await response.json();
        if (!Array.isArray(data.events) || !Array.isArray(data.bookings)) throw new Error('Invalid schedule data');

        const events = data.events.filter(item => item.date >= today).sort((a, b) => a.date.localeCompare(b.date));
        if (eventContainer) {
            if (!events.length) message(eventContainer, '開催日程は公式LINEでご確認ください。');
            events.forEach(item => {
                const card = document.createElement('article');
                card.className = 'glass-card rounded-2xl p-6 border border-white/10';
                card.append(label('p', dateLabel(item.date), 'text-sky-400 font-bold mb-2'));
                card.append(label('h4', item.title, 'text-white font-bold text-lg mb-2'));
                const details = [item.time, item.place, item.note].filter(Boolean).join(' / ');
                if (details) card.append(label('p', details, 'text-slate-300 text-sm leading-relaxed mb-3'));
                const link = label('a', '詳細は公式LINEへ →', 'text-sky-400 text-sm font-bold hover:text-sky-300');
                link.href = lineUrl;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                card.append(link);
                eventContainer.append(card);
            });
        }

        const byDate = new Map();
        data.bookings.filter(item => item.date >= today).forEach(item => {
            if (!byDate.has(item.date)) byDate.set(item.date, []);
            byDate.get(item.date).push(item);
        });
        if (bookingContainer) {
            if (!byDate.size) message(bookingContainer, '最新の空き枠は公式LINEでご確認ください。');
            [...byDate].sort(([a], [b]) => a.localeCompare(b)).forEach(([date, slots]) => {
                const card = document.createElement('div');
                card.className = 'bg-white/5 p-5 rounded-2xl border border-white/10 hover:border-sky-500/40 transition';
                card.append(label('h4', dateLabel(date), 'font-bold text-base text-sky-400 border-b border-white/10 pb-3 mb-4'));
                const rows = document.createElement('div');
                rows.className = 'space-y-2';
                slots.forEach(slot => {
                    const row = document.createElement('div');
                    row.className = 'flex items-center justify-between gap-2 bg-black/40 p-3 rounded-xl border border-white/5';
                    row.append(label('span', slot.time, 'text-xs sm:text-sm font-bold text-white'));
                    const available = slot.status === '空きあり';
                    row.append(label('span', available ? '◯ 空きあり' : `✕ ${slot.status}`,
                        `text-[11px] font-bold px-2 py-0.5 rounded-md ${available ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-700 text-slate-400'}`));
                    rows.append(row);
                });
                card.append(rows);
                bookingContainer.append(card);
            });
        }
    } catch (error) {
        console.error('Schedule could not be displayed', error);
        message(eventContainer, '開催日程は公式LINEでご確認ください。');
        message(bookingContainer, '最新の空き枠は公式LINEでご確認ください。');
    }
})();
