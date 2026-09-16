extern "C" void run_capture_controls();
extern "C" int capture_available();
int main() {
    if (!capture_available()) return 19;
    run_capture_controls();
    return 0;
}
