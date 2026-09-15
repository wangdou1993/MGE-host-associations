
#install.packages("vegan")


library(vegan)
library(ggplot2)

raw_abundance_matrix <- read.table("subtype-ARG-OAP.txt", header = TRUE, row.names = 1)
abundance_matrix <- t(raw_abundance_matrix)
meta_data <- read.table("metadata.txt", header = TRUE)

dist_matrix <- vegdist(abundance_matrix, method = "bray")

pcoa <- cmdscale(dist_matrix, eig = TRUE, k = 2)

pcoa_df <- data.frame(SampleID = row.names(pcoa$points),
                      PC1 = pcoa$points[, 1],
                      PC2 = pcoa$points[, 2],
                      Group = meta_data$Group)

test_result <- anosim(dist_matrix, meta_data$Group, permutations = 999)


groups <- unique(meta_data$Group)
color_mapping <- c(
  "IN" = "#F4C1E6", 
  "AS" = "#CEE7FD", 
  "EFF" = "#D5CBF0",
  "ADS" = "#B8CB5B" 
)

if (length(groups) > length(color_mapping)) {
  color_mapping <- rainbow(length(groups))
  names(color_mapping) <- groups
}


p <- ggplot(pcoa_df, aes(x = PC1, y = PC2, fill = Group)) +
  geom_point(size = 4, shape = 21, color = "black") +
  #geom_text(aes(label = SampleID), vjust = -1, size = 3, color = "black") +
  stat_ellipse(aes(color = Group), level = 0.95, 
               geom = "polygon", alpha = 0, linetype = 2, size = 0.5) +
  scale_fill_manual(values = color_mapping) +
  scale_color_manual(values = color_mapping) +
  labs(title = "PCoA with ANOSIM",
       x = paste0("PCoA1 (", round(pcoa$eig[1] / sum(pcoa$eig) * 100, 2), "%)"),
       y = paste0("PCoA2 (", round(pcoa$eig[2] / sum(pcoa$eig) * 100, 2), "%)"),
       caption = paste0("ANOSIM: R = ", round(test_result$statistic, 3),
                        ", p = ", test_result$signif)) +
  theme_bw() +
  theme(legend.title = element_blank(),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        legend.position = "right") +
  guides(fill = guide_legend(override.aes = list(shape = 21)))

print(p)

ggsave("pcoa_ARG-OAP-2026.pdf", plot = p, width = 5.5, height = 4, units = "in")


