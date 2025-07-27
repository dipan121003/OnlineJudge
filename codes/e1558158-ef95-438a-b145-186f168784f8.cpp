#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const long long INF = 1e9;

vector<int> minDistArr(vector<vector<int>>& g, int s, int l){
    vector<int> minDist(l+1, -1);
    queue<int> q;

    minDist[s] = 0;
    q.push(s);

    while(!q.empty()){
        int curr = q.front(); q.pop();
        for(int i: g[curr]){
            if(minDist[i] == -1){
                minDist[i] = minDist[curr] + 1;
                q.push(i);
            }
        }
    }

    return minDist;
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int C1, C2, C3, N, M;
    cin >> C1 >> C2 >> C3 >> N >> M;

    vector<vector<int>> adj(N+1);
    for(int i=0; i<M; i++){
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    auto minArrH = minDistArr(adj, 1, N);
    auto minArrW = minDistArr(adj, 2, N);
    auto minArrN = minDistArr(adj, N, N);

    long long minCost = INF;
    for(int i=1; i<=N; i++){
        if(minArrH[i] == -1 || minArrW[i] == -1 || minArrN[i] == -1){
            continue;
        }

        long long thisCost = minArrH[i]*C1 + minArrW[i]*C2 + minArrN[i]*C3;
        minCost = min(minCost, thisCost);
    }

    if(minCost == INF){
        cout << -1 << endl;
    } else {
        cout << minCost << endl;
    }

    return 0;
}