clearvars
close all
clc

%direction 1
osm_from_ankara = readtable('koridor_csv_files\kiz_pol.csv');
osm_from_ankara = TR_parse_sql_inquiry(osm_from_ankara);
osm_from_ankara = addvars(osm_from_ankara,ones(size(osm_from_ankara,1),1));

%direction 2
osm_to_ankara = readtable('koridor_csv_files\pol_kiz.csv');
osm_to_ankara = TR_parse_sql_inquiry(osm_to_ankara);
osm_to_ankara = addvars(osm_to_ankara,2*ones(size(osm_to_ankara,1),1));

osm=[osm_from_ankara;osm_to_ankara];

osm.Properties.VariableNames{3} = 'end_node';
osm.Properties.VariableNames{4} = 'given_length';
osm.Properties.VariableNames{12} = 'dir';
osm.segment_id = uint64(osm.segment_id);
osm.start_node = uint64(osm.start_node);
osm.end_node = uint64(osm.end_node);
osm.road_type = categorical(osm.road_type);
osm.dir = uint8(osm.dir);

osm.calc_length = diag(TR_get_distance([osm.startLat(:), osm.startLon(:)],[osm.endLat(:), osm.endLon(:)]));
% TR_get_distance(@(x) TR_get_distance([osm.startLat(1), osm.startLon(1)],[osm.endLat(1), osm.endLon(1)]));


% UPDATE 
% 2 TANE SEGMENT_ID = 1019 VAR
% 1049 SEGMENT_ID EKSÝK
osm.segment_id(317:end) = transpose(1:1:length(osm.segment_id(317:end)))+1000;


osm.distance_from_start = zeros(size(osm,1),1);
osm.distance_from_start(osm.dir == 1)  = cumsum(osm.calc_length((osm.dir == 1))) - osm.calc_length((osm.dir == 1));
osm.distance_from_start(osm.dir == 2)  = cumsum(osm.calc_length((osm.dir == 2))) - osm.calc_length((osm.dir == 2));



% save osm.mat osm