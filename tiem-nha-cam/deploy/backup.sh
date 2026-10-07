#!/usr/bin/env bash
# Sao lưu DB (snapshot an toàn khi app đang chạy) + ảnh upload, giữ 14 bản gần nhất.
# Cron hằng ngày lúc 3h:  0 3 * * * /home/ducdu/hermes-custom/tiem-nha-cam/deploy/backup.sh >> /home/ducdu/tnc-backup.log 2>&1
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${DATA_DIR:-$APP_DIR/data}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups/tiem-nha-cam}"
STAMP="$(date +%Y%m%d-%H%M)"
mkdir -p "$BACKUP_DIR"

python3 - "$DATA_DIR/app.db" "$BACKUP_DIR/app-$STAMP.db" <<'PY'
import sqlite3, sys
src = sqlite3.connect(sys.argv[1])
dst = sqlite3.connect(sys.argv[2])
src.backup(dst)   # online backup API — không cần dừng app
dst.close(); src.close()
PY
gzip -f "$BACKUP_DIR/app-$STAMP.db"
tar -czf "$BACKUP_DIR/uploads-$STAMP.tar.gz" -C "$DATA_DIR" uploads 2>/dev/null || true

ls -1t "$BACKUP_DIR"/app-*.db.gz 2>/dev/null | tail -n +15 | xargs -r rm -f
ls -1t "$BACKUP_DIR"/uploads-*.tar.gz 2>/dev/null | tail -n +15 | xargs -r rm -f
echo "[$(date)] backup OK → $BACKUP_DIR (app-$STAMP.db.gz)"
