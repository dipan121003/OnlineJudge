#include <iostream>
#include <vector>
#include <set>
using namespace std;
using ll = long long;

const ll INF = 1000000000000000000LL;

ll Dijkstra(vector<vector<pair<int,int>>>& g, int sou, int dest, int l){
    vector<ll> dist(l+1, INF);
    set<pair<ll,int>> s;

    dist[sou] = 0;
    s.insert({0,sou});

    while(!s.empty()){
        auto [d,u] = *s.begin(); s.erase(s.begin());
        for(auto [x,c]: g[u]){
            if(d+c < dist[x]){
                if(dist[x] != INF){
                    s.erase({dist[x],x});
                }
                dist[x] = d+c;
                s.insert({d+c,x});
            }
        }
    }

    return dist[dest];
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);

    int N,M;
    cin >> N >> M;

    vector<vector<pair<int,int>>> adj((N<<1)+2);
    for(int i=0; i<M; i++){
        int a,b,w;
        cin >> a >> b >> w;
        adj[a].push_back({b, w});

        adj[a+N].push_back({b+N, w});
        adj[a].push_back({b+N, w/2});
    }
    adj[(N<<1)].push_back({(N<<1)+1, 0});
    adj[N].push_back({(N<<1)+1, 0});

    ll ans = Dijkstra(adj, 1, (N<<1)+1, (N<<1)+1);
    cout << ans << endl;

    return 0;
}