const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('serverinfo')
        .setDescription('Sunucu hakkında genel bilgileri gösterir.'),
    async execute(interaction) {
        const { guild } = interaction;

        const embed = new EmbedBuilder()
            .setColor('#0099ff')
            .setTitle(`📊 ${guild.name} - Sunucu Bilgileri`)
            .setThumbnail(guild.iconURL({ dynamic: true }))
            .addFields(
                { name: '👑 Sunucu Sahibi', value: `<@${guild.ownerId}>`, inline: true },
                { name: '📅 Oluşturulma Tarihi', value: guild.createdAt.toLocaleDateString('tr-TR'), inline: true },
                { name: '👥 Üye Sayısı', value: guild.memberCount.toString(), inline: true },
                { name: '💬 Kanal Sayısı', value: guild.channels.cache.size.toString(), inline: true },
                { name: '🎭 Rol Sayısı', value: guild.roles.cache.size.toString(), inline: true },
                { name: '😃 Emoji Sayısı', value: guild.emojis.cache.size.toString(), inline: true },
                { name: '🆔 Sunucu ID', value: guild.id, inline: false }
            )
            .setFooter({ text: `Boost Seviyesi: ${guild.premiumTier}` })
            .setTimestamp();

        await interaction.reply({ embeds: [embed] });
    }
};
