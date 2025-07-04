#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <map>
#include <algorithm>

struct Component {
    std::string id;
    std::string type;
};

struct Input {
    std::string name;
    int index;
    bool value;
};

struct Connect {
    std::string from;
    int findex;
    std::string to;
    int tindex;
};

struct Output {
    std::string put;
    int kndex;
};

class Circuit {
private:
    std::vector<Component> components;
    std::vector<Input> inputs;
    std::vector<Connect> connections;
    Output output;
    std::unordered_map<std::string, std::vector<bool>> computedOutputs;

public:   

    void parseLine(const std::string& line) {
        std::istringstream ss(line);
        std::string word;
        ss >> word;

        if (word == "comp") {
            Component c;
            while (ss >> word) {
                if (word.find("id=") != std::string::npos)
                    c.id = word.substr(word.find("=")+1);
                else if (word.find("type=") != std::string::npos)
                    c.type = word.substr(word.find("=")+1);
            }
            components.push_back(c);
        } else if (word == "input") {
            Input in;
            while (ss >> word) {
                if (word.find("name=") != std::string::npos)
                    in.name = word.substr(word.find("=")+1);
                else if (word.find("index=") != std::string::npos)
                    in.index = std::stoi(word.substr(word.find("=")+1));
                else if (word.find("value=") != std::string::npos)
                    in.value = (word.substr(word.find("=")+1) == "1");
            }
            inputs.push_back(in);
        } else if (word == "connect") {
            Connect conn;
            while (ss >> word) {
                if (word.find("from=") != std::string::npos)
                    conn.from = word.substr(word.find("=")+1);
                else if (word.find("findex=") != std::string::npos)
                    conn.findex = std::stoi(word.substr(word.find("=")+1));
                else if (word.find("to=") != std::string::npos)
                    conn.to = word.substr(word.find("=")+1);
                else if (word.find("tindex=") != std::string::npos)
                    conn.tindex = std::stoi(word.substr(word.find("=")+1));
            }
            connections.push_back(conn);
        } else if (word == "Out") {
            ss >> word;
            output.put = word.substr(word.find("=")+1);
            ss >> word;
            output.kndex = std::stoi(word.substr(word.find("=")+1));
        }
    }

    void loadXML(const std::string& filename) {
        std::ifstream file("components/" + filename); // <-- changed
        std::string line;
        while (std::getline(file, line)) {
            parseLine(line);
        }
    }

    std::vector<bool> evaluate(const std::string& id) {
        if (computedOutputs.find(id) != computedOutputs.end()) {
            return computedOutputs[id];
        }

        // Check if id is an input
        std::vector<bool> inputVals;
        for (const auto& in : inputs) {
            if (in.name == id) {
                if (in.index >= inputVals.size())
                    inputVals.resize(in.index + 1, false);
                inputVals[in.index] = in.value;
            }
        }
        if (!inputVals.empty()) {
            computedOutputs[id] = inputVals;
            return inputVals;
        }

        Component* comp = nullptr;
        for (auto& c : components) {
            if (c.id == id) {
                comp = &c;
                break;
            }
        }
        if (!comp) {
            std::cerr << "Component not found: " << id << "\n";
            return {false};
        }

        std::vector<bool> inputValues;
        for (auto& conn : connections) {
            if (conn.to == id) {
                std::vector<bool> fromVals = evaluate(conn.from);
                if (conn.findex < fromVals.size()) {
                    inputValues.resize(std::max((int)inputValues.size(), conn.tindex + 1), false);
                    inputValues[conn.tindex] = fromVals[conn.findex];
                }
            }
        }

        for (auto& in : inputs) {
            if (in.name == id) {
                inputValues.resize(std::max((int)inputValues.size(), in.index + 1), false);
                inputValues[in.index] = in.value;
            }
        }

        std::vector<bool> results;

        if (comp->type == "AND") {
            bool res = true;
            for (bool v : inputValues) res &= v;
            results = {res};
        } else if (comp->type == "OR") {
            bool res = false;
            for (bool v : inputValues) res |= v;
            results = {res};
        } else if (comp->type == "NOT") {
            results = {inputValues.empty() ? true : !inputValues[0]};
        } else {
            // Load and evaluate subcircuit
            Circuit sub;
            sub.loadXML(comp->type + ".txt");

            for (size_t i = 0; i < inputValues.size(); ++i) {
                sub.inputs.push_back({comp->id, (int)i, inputValues[i]});
            }

            for (const Component& c : sub.components) {
                sub.evaluate(c.id);
            }

            results = sub.computedOutputs[sub.output.put];
        }

        computedOutputs[id] = results;
        return results;
    }

    bool getOutput() const {
        auto it = std::find_if(inputs.begin(), inputs.end(), [&](const Input& in) {
            return in.name == output.put && in.index == output.kndex;
        });

        if (it != inputs.end()) {
            return it->value;
        }

        return false;
    }

    void simulate() {
        std::vector<bool> result = evaluate(output.put);
        std::cout << "Output from " << output.put << " index " << output.kndex << ": "
                  << (output.kndex < result.size() ? result[output.kndex] : false) << "\n";
    }

    void saveComponent(const std::string& filename) {
        std::ofstream file("components/" + filename); // <-- changed
        for (const auto& c : components) {
            file << "comp id=" << c.id << " type=" << c.type << "\n";
        }
        for (const auto& i : inputs) {
            file << "input name=" << i.name << " index=" << i.index << " value=" << i.value << "\n";
        }
        for (const auto& c : connections) {
            file << "connect from=" << c.from << " findex=" << c.findex << " to=" << c.to << " tindex" << c.tindex << "\n";
        }
        file << "Out put=" << output.put << " kndex=" << output.kndex << "\n";
        std::cout << "Component saved to components/" << filename << "\n";
    }

};

int main() {
    Circuit circuit;
    circuit.loadXML("main.txt"); // This will now look in components/main.txt
    circuit.saveComponent("XOR.txt"); // This will now save to components/XOR.txt
    circuit.simulate();
    return 0;
}