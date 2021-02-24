clearvars
close all
clc

segments = load('input_data\osm.mat').osm;

% dir -- 1
% 29289705; milli kütüphane
% 276961615; konya yolu
% 288704314; armada
% 393950525; odtü
% 27046656; bilkent
% 2272351639; hacettepe
% 288241918; ümitköy
% 2389806681; çayyolu
% 493138684; çevreyolu
% 2380594397; çankayaüni
% 2381256503; kantar
% 2204797102; temelli
% 
% 
% dir -- 2
% 29451060; milli kütüphane
% 665879120; konya yolu
% 293438432; armada
% 29285802; odtü
% 29474304; bilkent
% 29474311; hacettepe
% 288241806; ümitköy
% 2389806684; çayyolu
% 205005044; çevreyolu
% 112372936; çankayaüni
% 112367659; temelli

names = {'milli kütüphane','konya yolu','armada','odtü','bilkent','hacettepe',...
    'ümitköy','çayyolu','çevreyolu','çankaya üni', 'kantar','temelli',...
    'milli kütüphane','konya yolu','armada','odtü','bilkent','hacettepe','ümitköy',...
    'çayyolu','çevreyolu','çankaya üni','temelli'};

nodes = [29289705, 276961615, 288704314, 393950525, 27046656, 2272351639,288241918,...
    2389806681, 493138684, 2380594397, 2381256503, 2204797102, 29451060, 665879120,...
    293438432, 29285802, 29474304, 29474311,288241806, 2389806684, 205005044, 112372936, 112367659];

markers = cell2table(transpose(names));
markers.Properties.VariableNames{1} = 'names';
markers.nodes = transpose(nodes);

[a,b] = ismember(markers.nodes, segments.start_node);

if sum(a == 0)
    error('segment nodelarında yok');
end


markers.dir = segments.dir(b);
markers.segment_id = segments.segment_id(b);
markers.distance_from_start = segments.distance_from_start(b);

corridor_length = max(sum(segments(segments.dir==2,:).calc_length) , sum(segments(segments.dir==1,:).calc_length));

markers.distance_from_kizilay = zeros(size(markers.nodes,1),1);
markers.distance_from_kizilay(markers.dir == 1) = markers.distance_from_start(markers.dir == 1);
markers.distance_from_kizilay(markers.dir == 2) = corridor_length - markers.distance_from_start(markers.dir == 2);

% save markers.mat markers