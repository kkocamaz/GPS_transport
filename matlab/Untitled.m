clearvars
clc
close all

seq = [1,2,3,5,1,2,3,3,1,2,3,2,1,4,1,1,4,1,2,4,3,2,1,2,3,4,1,1,5,4,3,3,4,5,1,2,4,5,1,2,4,5];

N=3;
M=5;

pi_matrix = ones(1,N) * 1/N;
A = ones(N,N) * 1/N;
B = ones(N,M) * 1/M;

T = size(seq,2);

max_iters = 999;
iters = 0;
oldLogProb = -10e9;

%the alpha-pass

% B MATRİSLERİNE BAK

alpha = zeros(T,N);
beta = zeros(T,N);
c = zeros(T,1);
gama = zeros(N,M,T);
gama2 = zeros(T,N);

%compute alpha
for i=1:1:N
    alpha(1,i) = pi_matrix(i)*B(i,seq(1));
    c(1) = c(1) + alpha(1,i);
end

%scale alpha
c(1) = 1/c(1);
for i=1:1:N
    alpha(1,i) = c(1) * alpha(1,i);
end

for t=2:1:T
    c(t) = 0;
    for i=1:1:N
        alpha(t,i) = 0;
        for j=1:1:N
            alpha(t,i) = alpha(t,i) + alpha(t-1,j)*A(j,i);
        end
        alpha(t,i) = alpha(t,i) * B(i,seq(t));
        c(t) = c(t) + alpha(t,i);
    end
    
    %scale alpha
    c(t) = 1 / c(t);
    for i=1:1:N
        alpha(t,i) = c(t) * alpha(t,i);
    end
end

% the beta pass
% let beta_T-1 = 1, scaled by cT-1 ???
% beta 1 olmuyor ??
for i=1:1:N
    beta(T,i) = c(T);
end

for t=T-1:-1:1
    for i=1:1:N
        beta(t,i) = 0;
        for j=1:1:N
            beta(t,i) = beta(t,i) + A(i,j)*B(j,seq(t+1))*beta(t+1,j);
        end
        beta(t,i) = c(t)*beta(t,i);
    end
end


% gama i,j,T
% gama2 t,i

for t=1:1:T-1
    denom=0;
    for i=1:1:N
        for j=1:1:N
            denom = denom + alpha(t,i)*A(i,j)*B(j,seq(t+1))*beta(t+1,j);
        end
    end
    for i=1:1:N
        gama2(t,i) = 0;
        for j=1:1:N
            gama(i,j,t) = (alpha(t,i)*A(i,j)*B(j,seq(t+1))*beta(t+1,j)) / denom;
            gama2(t,i) = gama2(t,i) + gama(i,j,t);
        end
    end
end

%special case for gama(T-1,i)

denom = 0;
for i=1:1:N
    denom = denom + alpha(T,i);
end
for i=1:1:N
    gama2(T,i) = alpha(T,i) / denom;
end


%re-estimate A, B, and pi

% re-estimate pi_matrix
for i=1:1:N
    pi_matrix(i) = gama2(1,i);
end


% re-estimate A
for i=1:1:N
    for j=1:1:N
        numer=0;
        denom=0;
        for t=1:1:T-1
            numer = numer + gama(i,j,t);
            denom = denom + gama2(t,i);
        end
        A(i,j) = numer/denom;
    end
end

% re-estimate B
for i=1:1:N
    for j=1:1:M
        numer=0;
        denom=0;
        for t=1:1:T
            if seq(t) == j
                numer = numer + gama2(t,i);
            else
                denom = denom + gama2(t,i);
            end
            denom = denom + gama2(t,i);
        end
        B(i,j) = numer/denom;
    end
end

% compute log of p(o|lambda)
logProb = 0;
for i=1:1:T
    logProb = logProb + log(c(i));
end
logProb = -1 * logProb;

% % to compare error
% iters = iters + 1;
% if (iters < maxiters  && logProb > oldLogProb)
%     oldLongProb = logProb;
%     % go iterate
% else
%     fprintf('completed')
% end
