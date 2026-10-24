import jdk.jfr.consumer.RecordedEvent;
import jdk.jfr.consumer.RecordingFile;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/** Summarizes Minecraft's periodic rolling-average tick event, not a per-tick latency distribution. */
public final class JfrSummary {
    public static void main(String[] args) throws Exception {
        List<Double> samples = new ArrayList<>();
        try (RecordingFile recording = new RecordingFile(Path.of(args[0]))) {
            while (recording.hasMoreEvents()) {
                RecordedEvent event = recording.readEvent();
                if (event.getEventType().getName().equals("minecraft.ServerTickTime")) {
                    // The persisted JFR field uses @Name("averageTickDuration"), not the Java member name.
                    samples.add(event.getDuration("averageTickDuration").toNanos() / 1_000_000.0D);
                }
            }
        }
        if (samples.isEmpty()) {
            throw new IllegalStateException("No minecraft.ServerTickTime samples in " + args[0]);
        }
        Collections.sort(samples);
        double mean = samples.stream().mapToDouble(Double::doubleValue).average().orElseThrow();
        double p95 = samples.get(Math.min(samples.size() - 1, (int) Math.ceil(samples.size() * 0.95) - 1));
        System.out.printf(Locale.ROOT,
                "{\"samples\":%d,\"mean_window_mspt\":%.6f,\"p95_window_mspt\":%.6f,\"max_window_mspt\":%.6f}%n",
                samples.size(), mean, p95, samples.get(samples.size() - 1));
    }
}
