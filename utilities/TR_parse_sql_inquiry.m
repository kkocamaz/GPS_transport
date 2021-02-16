function T = parse_sql_inquiry(T)
%UNTİTLED Summary of this function goes here
%   Detailed explanation goes here



% example:T.st_astext{1} = ['LINESTRING(32.8486566 39.914424,32.84617 39.914835)']

n=size(T,1);

T.startLat=zeros(n,1);
T.startLon=zeros(n,1);

T.endLat=zeros(n,1);
T.endLon=zeros(n,1);

for i=1:1:n
    key   = '(';
    index = strfind(T.st_astext{i}, key);
    T.startLon(i) = sscanf(T.st_astext{i}(index(1) + length(key):end), '%f', 1);
    key   = ' ';
    index = strfind(T.st_astext{i}, key);
    T.startLat(i) = sscanf(T.st_astext{i}(index(1) + length(key):end), '%f', 1);
    T.endLat(i) = sscanf(T.st_astext{i}(index(2) + length(key):end), '%f', 1);
    key   = ',';
    index = strfind(T.st_astext{i}, key);
    T.endLon(i) = sscanf(T.st_astext{i}(index(1) + length(key):end), '%f', 1);
end


end

