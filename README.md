# Local Dev Launcher

A small, dependency-free Python process orchestrator for repeatable local development stacks. Define several development commands in one JSON file, validate the configuration, launch them together, keep separate logs, and stop the stack cleanly with Ctrl+C.

> **Scope:** this is a local development helper, not a production process manager, container orchestrator, or service supervisor.

## Why it exists

Projects often require an API, frontend, worker, emulator, or static server to run together. Remembering several terminal commands and environment settings is error-prone. Local Dev Launcher keeps that intent in a reviewable project file without requiring Docker, Node.js tooling, or a background daemon.

## Features

- Starts multiple processes in declared order.
- Commands are argument arrays and run with `shell=False`.
- Per-process working directory and environment overrides.
- Optional startup grace period (`ready_after`) to catch early exits.
- Optional processes may fail to start without taking down required services.
- One UTF-8 log file per process.
- Graceful reverse-order shutdown, followed by forced termination after a timeout.
- `check` validates configuration without launching commands.
- Text or JSON startup status.
- Python API plus `dev-launch` CLI.
- No runtime dependencies, network calls, telemetry, or daemon.

## Preview

```text
$ dev-launch check dev-launch.json
OK: 3 process(es) configured

$ dev-launch run dev-launch.json
started api (pid 18320)
started web (pid 18344)
started worker (pid 18402)
Press Ctrl+C to stop the stack.
```

For screenshots, capture the terminal after `dev-launch run`; the project intentionally has no graphical interface.

## Requirements

- Python 3.10+
- The programs referenced by your configuration must already be installed.

## Installation

```bash
git clone https://github.com/rad03i2/local-dev-launcher.git
cd local-dev-launcher
python -m venv .venv
python -m pip install -e .
```

Activate the virtual environment using the command appropriate for your shell, then verify:

```bash
dev-launch --version
```

## Configuration

Create `dev-launch.json` in your project root:

```json
{
  "processes": [
    {
      "name": "api",
      "command": ["python", "-m", "http.server", "8080"],
      "cwd": ".",
      "ready_after": 0.5,
      "optional": false,
      "env": {"APP_ENV": "development"}
    }
  ]
}
```

`name` must be unique. `command` must be a non-empty array of arguments. `cwd` is resolved relative to the configuration file. `env` augments the current environment. `ready_after` accepts 0–300 seconds. `optional` defaults to false.

Do **not** put secrets in the JSON file. Environment overrides are intended for non-sensitive development settings.

## Usage

```bash
# Validate only; no child process is started
dev-launch check dev-launch.json

# Start and supervise the stack
dev-launch run dev-launch.json

# Put logs elsewhere
dev-launch run dev-launch.json --log-dir var/dev-logs

# Machine-readable startup state
dev-launch run dev-launch.json --json

# Module form
python -m local_dev_launcher check dev-launch.json
```

Logs default to `.dev-logs/<process-name>.log`. If a required process exits non-zero, the launcher exits with that code after shutting down the stack. Ctrl+C exits with code 130.

## Python API

```python
from local_dev_launcher import Launcher, load_config

specs = load_config("dev-launch.json")
with Launcher(specs) as launcher:
    print(launcher.status())
    exit_code = launcher.wait()
```

## Project structure

```text
src/local_dev_launcher/  core, CLI, package entry point
tests/                   configuration, lifecycle, CLI tests
examples/                safe example configuration
.github/workflows/       cross-platform CI
CONTRIBUTING.md           contributor guide
SECURITY.md               security model and reporting
```

## Testing

```bash
python -m pip install -e .
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Tests include real short-lived child-process execution and termination behavior; they do not require network access.

## Security & privacy

Configuration is executable intent: review it before running. Shell command strings are rejected and `shell=False` is always used. The application sends no telemetry and makes no network requests itself, although configured child programs can. Child output is persisted in log files and may contain sensitive application output.

## Limitations

- No dependency graph or automatic service restart.
- `ready_after` is a time-based early-exit check, not an HTTP/TCP health probe.
- No interactive TUI/GUI and no log multiplexing to the terminal.
- Environment variable interpolation and `.env` parsing are intentionally absent.
- It is not intended to keep production workloads alive.

## Optional roadmap

Potential future additions include explicit health checks, dependency ordering, and opt-in restart policies. They are not claimed as current features.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security-sensitive reports should follow [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)

---

# Local Dev Launcher — العربية

أداة Python صغيرة بلا اعتماديات تشغيل خارجية لتشغيل مجموعة خدمات التطوير المحلي من ملف JSON واحد، والتحقق من الإعداد، وحفظ سجل مستقل لكل عملية، ثم إيقاف المجموعة بصورة منظمة عند الضغط على Ctrl+C.

> **النطاق:** الأداة مخصصة للتطوير المحلي، وليست مدير عمليات للإنتاج أو بديلًا عن Docker أو أنظمة إدارة الخدمات.

## لماذا هذا المشروع؟

تحتاج مشاريع كثيرة إلى تشغيل API وواجهة وWorker أو خادم ملفات معًا. بدل تذكر عدة أوامر وفتح نوافذ طرفية متعددة، يحفظ المشروع أوامر التطوير في ملف واضح يمكن مراجعته ومشاركته مع الفريق.

## المزايا

- تشغيل عدة عمليات بالترتيب المعرّف.
- تنفيذ الأوامر كمصفوفة arguments مع `shell=False` لخفض مخاطر حقن أوامر shell.
- مجلد عمل ومتغيرات بيئة إضافية لكل عملية.
- فترة انتظار اختيارية لاكتشاف الخروج المبكر.
- دعم العمليات الاختيارية التي لا توقف المجموعة إذا تعذر تشغيلها.
- سجل UTF-8 مستقل لكل عملية.
- إيقاف منظم بالترتيب العكسي ثم قتل العملية إذا تجاوزت مهلة الإيقاف.
- أمر `check` يفحص الإعداد من دون تشغيل أي برنامج.
- خرج نصي أو JSON للحالة عند التشغيل.
- CLI وPython API.
- لا شبكة ولا telemetry ولا daemon ولا اعتماديات runtime.

## المعاينة

```text
$ dev-launch check dev-launch.json
OK: 3 process(es) configured

$ dev-launch run dev-launch.json
started api (pid 18320)
started web (pid 18344)
started worker (pid 18402)
Press Ctrl+C to stop the stack.
```

لا توجد واجهة رسومية؛ يمكن أخذ لقطة شاشة للطرفية بعد التشغيل عند الحاجة إلى صورة للمشروع.

## المتطلبات والتثبيت

يتطلب Python 3.10 أو أحدث، إضافة إلى البرامج التي تضعها أنت داخل الإعداد.

```bash
git clone https://github.com/rad03i2/local-dev-launcher.git
cd local-dev-launcher
python -m venv .venv
python -m pip install -e .
dev-launch --version
```

## الإعداد والاستخدام

أنشئ `dev-launch.json` كما في المثال الموجود في `examples/dev-launch.json`. يجب أن يكون `name` فريدًا، وأن تكون `command` مصفوفة نصوص غير فارغة، ويُحسب `cwd` نسبة إلى مكان ملف الإعداد. لا تضع كلمات مرور أو مفاتيح API داخل الملف.

```bash
dev-launch check dev-launch.json
dev-launch run dev-launch.json
dev-launch run dev-launch.json --log-dir var/dev-logs
dev-launch run dev-launch.json --json
python -m local_dev_launcher check dev-launch.json
```

السجلات الافتراضية في `.dev-logs/`. إذا خرجت عملية مطلوبة برمز غير صفري يعيد المشغل ذلك الرمز بعد إيقاف المجموعة، وCtrl+C يعيد 130.

## Python API

```python
from local_dev_launcher import Launcher, load_config

specs = load_config("dev-launch.json")
with Launcher(specs) as launcher:
    print(launcher.status())
    exit_code = launcher.wait()
```

## بنية المشروع

```text
src/local_dev_launcher/  المحرك وCLI ونقطة تشغيل الحزمة
tests/                   اختبارات الإعداد ودورة حياة العمليات وCLI
examples/                مثال إعداد آمن
.github/workflows/       CI متعدد الأنظمة
CONTRIBUTING.md           دليل المساهمة
SECURITY.md               نموذج الأمان والإبلاغ
```

## الاختبارات

```bash
python -m pip install -e .
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

تتضمن الاختبارات تشغيل عملية قصيرة فعلية واختبار الإيقاف، ولا تحتاج إلى الإنترنت.

## الأمان والخصوصية

ملف الإعداد يمثل نية تنفيذ أوامر، لذلك راجعه قبل التشغيل. ترفض الأداة أوامر shell النصية وتستخدم `shell=False`. لا ترسل الأداة بيانات أو telemetry ولا تجري اتصالات شبكة بنفسها، لكن البرامج التي تختار تشغيلها قد تفعل ذلك. وقد تحتوي ملفات السجل على خرج حساس من تطبيقاتك.

## القيود

لا توجد حاليًا خريطة اعتماديات بين الخدمات أو إعادة تشغيل تلقائية. `ready_after` فحص زمني للخروج المبكر وليس health check شبكيًا. لا توجد GUI/TUI أو قراءة `.env` أو interpolation لمتغيرات البيئة. المشروع ليس مخصصًا لأحمال الإنتاج.

## تطوير اختياري مستقبلاً

يمكن إضافة health checks صريحة وترتيب اعتماديات وسياسات restart اختيارية مستقبلًا؛ وهذه ليست مزايا موجودة في الإصدار الحالي.

## المساهمة والترخيص

راجع [CONTRIBUTING.md](CONTRIBUTING.md)، واتبع [SECURITY.md](SECURITY.md) للمشكلات الأمنية. المشروع مرخص بترخيص MIT؛ راجع [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: [@rad03i2](https://github.com/rad03i2)
