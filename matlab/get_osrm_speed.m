clearvars
close all
clc

out = load('output_data\osrm_output.mat').out;
out.isUsedAug = logical(load('output_data\aug_output.mat').isUsedAug);

%cleaning
out = out(out.isUsedAug,:);

out.space_distance = NaN(size(out,1),1);
out.time_distance = NaN(size(out,1),1);
out.speed = NaN(size(out,1),1);


arac_list = unique(out.arac_id);

for i=1:1:length(arac_list)
    route_list = unique(out(out.arac_id == arac_list(i),:).route_id);
    for j=1:1:length(route_list)
%         get_data = matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).speed;
%         get_data = get_arac(get_arac.route_id == route_list(j),:);
%         matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).speed(1:end-1) = 1e-3*diff(matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).distance_from_start) ./ hours(diff(matched(matched.arac_id == arac_list(i) & matched.route_id == route_list(j),:).raw_time));
        index = out.arac_id == arac_list(i) & out.route_id == route_list(j);

        out(index, :).space_distance(1:end-1) = diff(out(out.arac_id == arac_list(i) & out.route_id == route_list(j),:).distance_from_start);
        out(index, :).time_distance(1:end-1) = hours(diff(out(out.arac_id == arac_list(i) & out.route_id == route_list(j),:).raw_time));

    end
end

out.speed = 1e-3 * out.space_distance ./ out.time_distance;