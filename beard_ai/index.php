<?php
$mappingPath = __DIR__ . '/mapping.json';
$uploadDir = __DIR__ . '/upload';

if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0775, true);
}

$mapping = json_decode((string) file_get_contents($mappingPath), true) ?: [];
$error = null;
$result = null;
$uploadedWebPath = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $savedPath = null;

    if (!empty($_POST['camera_image'])) {
        $raw = $_POST['camera_image'];
        if (preg_match('/^data:image\/(png|jpeg|jpg);base64,/', $raw, $m)) {
            $raw = substr($raw, strpos($raw, ',') + 1);
            $decoded = base64_decode(str_replace(' ', '+', $raw), true);
            if ($decoded !== false) {
                $ext = $m[1] === 'jpeg' ? 'jpg' : $m[1];
                $filename = 'camera_' . date('Ymd_His') . '_' . bin2hex(random_bytes(4)) . '.' . $ext;
                $savedPath = $uploadDir . '/' . $filename;
                file_put_contents($savedPath, $decoded);
            }
        }
    } elseif (!empty($_FILES['face_image']['name']) && is_uploaded_file($_FILES['face_image']['tmp_name'])) {
        $allowed = ['image/jpeg' => 'jpg', 'image/png' => 'png', 'image/jpg' => 'jpg'];
        $mime = mime_content_type($_FILES['face_image']['tmp_name']);
        if (!isset($allowed[$mime])) {
            $error = 'Only JPG and PNG are supported.';
        } else {
            $filename = 'upload_' . date('Ymd_His') . '_' . bin2hex(random_bytes(4)) . '.' . $allowed[$mime];
            $savedPath = $uploadDir . '/' . $filename;
            move_uploaded_file($_FILES['face_image']['tmp_name'], $savedPath);
        }
    } else {
        $error = 'Please upload an image or capture one from the camera.';
    }

    if ($savedPath && !$error) {
        $uploadedWebPath = 'upload/' . basename($savedPath);

        $python = 'python3';
        $cmd = $python . ' ' . escapeshellarg(__DIR__ . '/classify_hairstyle.py') . ' ' . escapeshellarg($savedPath);
        $output = shell_exec($cmd);
        $prediction = json_decode((string) $output, true);

        if (!is_array($prediction) || empty($prediction['hairstyle'])) {
            $error = 'Unable to classify hairstyle.';
        } else {
            $hairstyle = $prediction['hairstyle'];
            if (!isset($mapping[$hairstyle])) {
                $error = 'No beard mapping found for hairstyle: ' . htmlspecialchars($hairstyle);
            } else {
                $choice = $mapping[$hairstyle];
                $result = [
                    'hairstyle' => $hairstyle,
                    'label' => $choice['label'],
                    'beard_style' => $choice['beard_style'],
                    'image' => 'dataset/' . $choice['length_group'] . '/' . ($choice['image_file'] ?? ($choice['beard_style'] . '.svg')),
                ];
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Beard AI Recommender</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <div class="container">
    <header class="header">
      <div class="brand">🧔 Beard AI Recommender</div>
      <div class="badge">Upload or Camera Input</div>
    </header>

    <div class="grid">
      <section class="card">
        <h2>Analyze Your Hairstyle</h2>
        <p>Upload a face photo or capture directly from your webcam to get a beard recommendation.</p>

        <form method="POST" enctype="multipart/form-data">
          <label for="face_image">Upload image</label>
          <input id="face_image" type="file" name="face_image" accept="image/png,image/jpeg" />

          <input type="hidden" name="camera_image" id="camera_image" />
          <div class="actions">
            <button type="submit" class="btn">Recommend Beard</button>
            <button type="button" class="btn secondary" id="captureBtn">Capture from Camera</button>
          </div>
        </form>

        <div style="margin-top:12px;">
          <video id="video" autoplay playsinline></video>
          <canvas id="canvas" style="display:none;"></canvas>
        </div>
      </section>

      <section class="card">
        <h3>Recommendation Result</h3>
        <p>After analysis, your suggested beard style appears here.</p>

        <?php if ($error): ?>
          <div class="result" style="border-color:#924444;background:rgba(239,68,68,.14);color:#ffd6d6;">
            <?php echo htmlspecialchars($error); ?>
          </div>
        <?php elseif ($result): ?>
          <div class="result">
            <div><strong>Detected Hairstyle:</strong> <?php echo htmlspecialchars($result['hairstyle']); ?></div>
            <div><strong>Suggested Beard:</strong> <?php echo htmlspecialchars($result['label']); ?></div>
            <div><strong>Source Image:</strong> <?php echo htmlspecialchars($uploadedWebPath ?? 'N/A'); ?></div>
            <img class="preview" src="<?php echo htmlspecialchars($result['image']); ?>" alt="Recommended beard style" />
          </div>
        <?php else: ?>
          <img class="preview" src="dataset/medium/full_beard.svg" alt="Sample beard style" />
        <?php endif; ?>
      </section>
    </div>

    <div class="footer">Dataset folders: short / medium / long (SVG assets, no binary files) • Mapping powered by <code>mapping.json</code></div>
  </div>

  <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const cameraField = document.getElementById('camera_image');

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = stream;
      } catch (e) {
        console.warn('Camera access not granted or unavailable.', e);
      }
    }

    captureBtn.addEventListener('click', () => {
      if (!video.videoWidth || !video.videoHeight) {
        alert('Camera is not ready yet. Allow access and try again.');
        return;
      }
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      cameraField.value = canvas.toDataURL('image/jpeg', 0.9);
      alert('Captured! Now click "Recommend Beard" to analyze.');
    });

    startCamera();
  </script>
</body>
</html>
