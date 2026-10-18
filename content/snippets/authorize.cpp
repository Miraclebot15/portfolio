#include <iostream>
#include <string>
#include <vector>

struct Action {
    std::string name;
    bool sensitive = false;
};

// A model may propose an action. It may not authorize itself.
bool authorize(const Action& a, bool approved = false) {
    return !a.sensitive || approved;
}

int main() {
    std::vector<Action> plan = {{"read_file"}, {"send_payment", true}};

    for (const auto& step : plan) {
        const char* verdict = authorize(step) ? "run" : "needs approval";
        std::cout << step.name << " -> " << verdict << "\n";
    }
}
