#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

const int INF = -1e9;

int main() {
    int n, m;
    cin >> n >> m;

    vector<vector<int>> graph(n + 1);
    vector<int> in_degree(n + 1, 0);
    vector<int> dp(n + 1, INF);      // dp[i] = max towns visited ending at i
    vector<int> parent(n + 1, -1);   // to reconstruct path (optional)

    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        graph[u].push_back(v);
        in_degree[v]++;
    }

    queue<int> q;

    // Topological sort queue start
    for (int i = 1; i <= n; ++i)
        if (in_degree[i] == 0)
            q.push(i);

    dp[1] = 1; // Starting from town 1, 1 town is visited

    while (!q.empty()) {
        int u = q.front();
        q.pop();

        for (int v : graph[u]) {
            if (dp[u] + 1 > dp[v]) {
                dp[v] = dp[u] + 1;
                parent[v] = u;
            }

            in_degree[v]--;
            if (in_degree[v] == 0)
                q.push(v);
        }
    }

    if (dp[n] < 0) {
        cout << -1 << endl;
    } else {
        cout << dp[n] << endl;
    }

    return 0;
}