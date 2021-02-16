% aynı kod gather_OSRMoutput dosyasında da bulunabilir.
% aynı rota içindeki map edilememiş datalardan rotayı ikiye ayırır.

clearvars
% clc

aq=[0,0,0,1,1,0,0,0,0,1,1,0,1,0,1,0,0,0];
aq = transpose(aq);

routes = [ones(length(aq)/3,1) ; 2*ones(length(aq)/3,1); 3*ones(length(aq)/3,1)];
% aq = horzcat(aq, ones(length(aq),1));
aq = horzcat(aq, routes);
% aq = [0,0,0,0];
flag = true;
while flag && size(aq,1) > 1
    if aq(1,1) == 0
        aq(1,:) = [];
    else
        flag = false;
    end
end

f = aq(:,1) == 0;
df = diff(aq(:,1) == 0);
df = [0; df];

%arka arkaya olan sıfırları sil.
%ilk sıfır haricindekileri siler.
%assumaption: ilk eleman 1
aq(f == 1 & df == 0,:) = [];

f2 = find(aq(:,1) == 0);
f2 = [1; f2];

for i=1:1:length(f2) - 1 
    aq(f2(i):end,2) = aq(f2(i):end,2) + 1;
end

aq(f2(2:end),:) = [];