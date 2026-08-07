export function formatAbsoluteTime(isoString: string): string {
    const d = new Date(isoString);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export function formatRelativeTime(isoString: string): string {
    const now = Date.now();
    const past = new Date(isoString).getTime();
    const seconds = Math.floor((now - past) / 1000);

    if (seconds < 60) {
        return "just now";
    }

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
        return `${minutes} ${minutes === 1 ? "minute" : "minutes"} ago`;
    }

    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
        return `${hours} ${hours === 1 ? "hour" : "hours"} ago`;
    }

    // Approximating month as 30 days for simplicity
    const days = Math.floor(hours / 24);
    if (days < 30) {
        return `${days} ${days === 1 ? "day" : "days"} ago`;
    }

    const months = Math.floor(days / 30);
    if (months < 12) {
        return `${months} ${months === 1 ? "month" : "months"} ago`;
    }

    const years = Math.floor(months / 12);
    return `${years} ${years === 1 ? "year" : "years"} ago`;
}