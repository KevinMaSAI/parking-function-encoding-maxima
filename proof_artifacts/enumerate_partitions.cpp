// SPDX-License-Identifier: MIT
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

using Count = std::uint64_t;
int n;
std::vector<int> values;
std::vector<Count> counts, weights;
std::vector<int> powers3;

std::string decode(int code) {
    std::string answer;
    for (int i=0; i<n-1; ++i) {
        answer.push_back("ADT"[code%3]);
        code /= 3;
    }
    return answer;
}

Count weight(int cuts) {
    std::vector<int> composition;
    int last=0;
    for (int i=1; i<=n; ++i) {
        if (i==n || (cuts & (1<<(i-1)))) {
            composition.push_back(i-last);
            last=i;
        }
    }
    std::vector<Count> current(n+1), next(n+1);
    current[0]=1;
    int used=0;
    for (int size:composition) {
        std::fill(next.begin(),next.end(),0);
        Count prefix=0;
        for (int value=1; value<=used+1; ++value) {
            prefix+=current[value-1];
            next[value]=prefix;
        }
        current.swap(next);
        used+=size;
    }
    return std::accumulate(current.begin(),current.end(),Count(0));
}

void visit(unsigned remaining, int level, int used, int cuts) {
    if (!remaining) {
        int code=0;
        for (int i=0;i<n-1;++i) {
            int digit=values[i]<values[i+1]?0:values[i]>values[i+1]?1:2;
            code+=digit*powers3[i];
        }
        counts[code]+=weights[cuts];
        return;
    }
    for (unsigned subset=remaining; subset; subset=(subset-1)&remaining) {
        for (unsigned bits=subset;bits;bits&=bits-1)
            values[__builtin_ctz(bits)]=level;
        int filled=used+__builtin_popcount(subset);
        int nextcuts=cuts|(filled<n?1<<(filled-1):0);
        visit(remaining^subset,level+1,filled,nextcuts);
    }
}

int main(int argc, char** argv) {
    int maxn=argc>1?std::stoi(argv[1]):9;
    std::string outdir=argc>2?argv[2]:"proof_artifacts";
    for (n=1;n<=maxn;++n) {
        auto start=std::chrono::steady_clock::now();
        values.assign(n,0);
        powers3.assign(n,1);
        for (int i=1;i<n;++i) powers3[i]=3*powers3[i-1];
        counts.assign(powers3[n-1],0);
        weights.resize(1<<(n-1));
        for (int mask=0;mask<(1<<(n-1));++mask) weights[mask]=weight(mask);
        visit((1u<<n)-1,1,0,0);
        std::ofstream file(outdir+"/counts_n"+std::to_string(n)+".json");
        file << "{\n";
        Count total=0, best=0, tie_best=0;
        std::vector<int> order(counts.size());
        std::iota(order.begin(),order.end(),0);
        std::sort(order.begin(),order.end(),[](int a,int b) {return counts[a]>counts[b];});
        for (int i=0;i<int(counts.size());++i) {
            auto w=decode(i);
            total+=counts[i];
            best=std::max(best,counts[i]);
            if(w.find('T')!=std::string::npos) tie_best=std::max(tie_best,counts[i]);
            file << "  \""<<w<<"\": "<<counts[i]<<(i+1<int(counts.size())?",":"")<<"\n";
        }
        file << "}\n";
        double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
        std::cout << "{\"n\":"<<n<<",\"total\":"<<total<<",\"maximum\":"<<best
                  <<",\"maximum_with_T\":"<<tie_best<<",\"maximizers\":[";
        bool first=true;
        for (int i:order) if(counts[i]==best) {
            if(!first) std::cout<<",";
            std::cout<<"\""<<decode(i)<<"\"";
            first=false;
        }
        std::cout << "],\"top\":[";
        first=true;
        for(int rank=0;rank<std::min(12,int(order.size()));++rank) {
            int i=order[rank];
            if(!first) std::cout<<",";
            std::cout<<"[\""<<decode(i)<<"\","<<counts[i]<<"]";
            first=false;
        }
        std::cout<<"],\"seconds\":"<<seconds<<"}"<<std::endl;
    }
}
