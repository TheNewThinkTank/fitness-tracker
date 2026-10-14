import gzip
import subprocess
import sys

from src.utils.config import PROJECT_ROOT


def test_file_logs_rotate_compress_and_keep_five_archives(tmp_path):
    result = subprocess.run(
        [sys.executable, "-c", (
            "import sys\n"
            "from src.utils.logger_config import logger, setup_logger\n"
            "original_add = logger.add\n"
            "def small_rotation(sink, **options):\n"
            "    if 'rotation' in options:\n"
            "        options['rotation'] = 512\n"
            "    return original_add(sink, **options)\n"
            "logger.add = small_rotation\n"
            "setup_logger(log_dir=sys.argv[1])\n"
            "for number in range(20):\n"
            "    logger.debug('Record {}: {}', number, 'x' * 300)\n"
            "logger.remove()\n"
        ), str(tmp_path)],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    )

    assert result.stderr == ""
    assert (tmp_path / "app.log").is_file()
    archives = list(tmp_path.glob("app.*.log.gz"))
    assert len(archives) == 5
    assert len(list(tmp_path.iterdir())) == 6
    assert "Record 19:" in (tmp_path / "app.log").read_text(encoding="utf-8")
    assert all("Record " in gzip.decompress(path.read_bytes()).decode() for path in archives)
